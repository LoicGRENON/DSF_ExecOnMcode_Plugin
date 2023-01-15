#!/usr/bin/python3

import json
import subprocess
import traceback
from pathlib import Path

from dsf.commands.code import CodeType
from dsf.connections import CommandConnection, InterceptConnection, InterceptionMode
from dsf.object_model.messages import MessageType
from dsf.object_model.state.log_level import LogLevel

from http_endpoints import custom_http_endpoints
from MCodeAction import MCodeAction


DEFAULT_FILTERS = ["M1200"]
PLUGIN_NAME = "ExecOnMcode"


def __get_action_for_code(actions, received_code):
    for action in actions:
        if action.cmd_code == received_code:
            return action


def __get_filters_from_actions(actions):
    filters = [a.cmd_code for a in actions]
    filters.extend(DEFAULT_FILTERS)
    return filters


def __update_interception_filters(intercept_connection):
    actions = get_actions_from_config()
    filters = __get_filters_from_actions(actions)
    msg = f"{PLUGIN_NAME}: Interception filters successfully updated"
    intercept_connection.resolve_code(MessageType.Success, msg)
    intercept_connection.close()
    intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters)
    intercept_connection.connect()
    return intercept_connection, filters, actions


def __do_action_for_code(intercept_connection, actions, code):
    error_msg = ""
    out = None
    action = __get_action_for_code(actions, code.short_str())
    if not action or not action.cmd_enabled:
        intercept_connection.ignore_code()
        return
    try:
        action_command = str(action.cmd_command)

        # if the m-code was passed with an argument, append that argument to the system command
        parameters = ''.join([str(p) for p in code.parameters])
        if len(parameters):
            action_command += ' ' + parameters

        out = subprocess.run(action_command,
                             shell=True,
                             timeout=action.cmd_timeout,
                             capture_output=True,
                             text=True)
    except subprocess.TimeoutExpired as e:
        error_msg = f"Timeout expired on `{e.cmd}`."
        if e.output:
            error_msg += f"\nOutput was: {e.output}"

    # Resolve the received code and return result
    if error_msg:
        intercept_connection.resolve_code(MessageType.Error, error_msg)
    else:
        # Display the command output if not explicitly requested to be hidden
        msg = f"[{PLUGIN_NAME}]: {out.stdout}" if out and out.stdout and not action.cmd_capture_output else None
        intercept_connection.resolve_code(MessageType.Success, msg)


def intercept_mcodes(actions):
    filters = __get_filters_from_actions(actions)
    intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters)
    intercept_connection.connect()

    try:
        while True:
            # Wait for a code to arrive
            code = intercept_connection.receive_code()

            # Check for the type of the code
            if code.type != CodeType.MCode:
                intercept_connection.ignore_code()
                continue

            if code.majorNumber == 1200:  # Update interception filters
                intercept_connection, filters, actions = __update_interception_filters(intercept_connection)
            elif code.short_str() in filters:  # Do action from JSON file
                __do_action_for_code(intercept_connection, actions, code)
            else:
                # We did not handle it so we ignore it and it will be continued to be processed
                intercept_connection.ignore_code()
    except Exception as e:
        print("Closing connection: ", e)
        traceback.print_exc()
        intercept_connection.close()


def write_message(msg, msgType=MessageType.Success, loglvl=LogLevel.Info):
    cmd_conn.write_message(msgType, f"{PLUGIN_NAME}: {msg}", True, loglvl)


def get_actions_from_config():
    actions = []
    # Use DSF API to get the physical path to the configuration file
    res = cmd_conn.resolve_path(f"0:/sys/{PLUGIN_NAME}/{PLUGIN_NAME}.json")
    filter_filepath = Path(res.result)
    if not filter_filepath.is_file():
        # Create missing parent directories
        filter_filepath.parent.mkdir(parents=True, exist_ok=True)
        # Create a blank default file as example
        default_file_data = [
            {
                'cmd_code': 'M1201',
                'cmd_name': 'Echo test',
                'cmd_command': f"echo 'If you can see this, it means {PLUGIN_NAME} is working !'",
                'cmd_timeout': 30,
                'cmd_capture_output': False,
                'cmd_enabled': True
            },
            {
                'cmd_code': 'M1202',
                'cmd_name': 'Python script example - Top',
                'cmd_command': "python3 /opt/dsf/sd/sys/ExecOnMcode/top-example.py",
                'cmd_timeout': 30,
                'cmd_capture_output': False,
                'cmd_enabled': True
            }
        ]
        with open(filter_filepath, 'w') as fp:
            fp.write(json.dumps(default_file_data, indent=4))

    with open(filter_filepath) as fp:
        try:
            json_filter = json.load(fp)
        except json.decoder.JSONDecodeError as e:
            json_filter = []
            write_message(e, MessageType.Error, LogLevel.Warn)
        for action in json_filter:
            if action['cmd_code'] in DEFAULT_FILTERS:
                write_message(
                    f"{action['cmd_code']} is a reserved filter and thus it can't be used.",
                    MessageType.Error,
                    LogLevel.Warn)
                continue
            try:
                actions.append(MCodeAction(action))
            except KeyError as e:
                write_message(e, MessageType.Error, LogLevel.Warn)
    return actions


if __name__ == "__main__":
    endpoints = []
    cmd_conn = CommandConnection()
    try:
        cmd_conn.connect()
        endpoints = custom_http_endpoints(cmd_conn)
        intercept_mcodes(get_actions_from_config())
    finally:
        for endpoint in endpoints:
            endpoint.close()
        cmd_conn.close()
