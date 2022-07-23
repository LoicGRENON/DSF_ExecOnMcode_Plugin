#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
import traceback
from pathlib import Path

from dsf.connections import InterceptConnection
from dsf.commands.basecommands import MessageType
from dsf.commands.code import CodeType
from dsf.initmessages.clientinitmessages import InterceptionMode

from MCodeAction import MCodeAction


# TODO: get the path from DSF config
DSF_PLUGINS_DIR = Path('/opt/dsf/plugins')
DEFAULT_FILTERS = ["M1200"]
PLUGIN_NAME = "ExecOnMcode"


def __get_action_for_code(actions, received_code):
    for action in actions:
        if action.code == received_code:
            return action


def __get_filters_from_actions(actions):
    filters = [a.code for a in actions]
    filters.extend(DEFAULT_FILTERS)
    return filters


def intercept_mcodes(actions):
    filters = __get_filters_from_actions(actions)
    # TODO: Set InterceptionMode and debug from settings
    intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters, debug=True)
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
                actions = get_actions_from_config()
                filters = __get_filters_from_actions(actions)
                msg = f"{PLUGIN_NAME}: Interception filters successfully updated"
                intercept_connection.resolve_code(MessageType.Success, msg)
                intercept_connection.close()
                # TODO: Set InterceptionMode and debug from settings
                intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters, debug=True)
                intercept_connection.connect()
            elif code.short_str() in filters:  # Do actions from JSON file
                error_msg = ""
                out = None
                action = __get_action_for_code(actions, code.short_str())
                if not action:
                    intercept_connection.ignore_code()
                    continue
                if action.flush:
                    # Flush the code's channel to be sure we are being in sync with the machine
                    success = intercept_connection.flush(code.channel)
                    if not success:
                        print("Flush failed")
                        intercept_connection.cancel_code()
                        continue
                # TODO: use user
                try:
                    out = subprocess.run(action.cmd,
                                         shell=True,
                                         timeout=action.timeout,
                                         capture_output=action.capture_output,
                                         text=True)
                except subprocess.TimeoutExpired as e:
                    error_msg = f"Timeout expired on `{e.cmd}`."
                    if action.capture_output and e.output:
                        error_msg += f"\nOutput was: {e.output}"

                # Resolve the received code and return result
                if error_msg:
                    intercept_connection.resolve_code(MessageType.Error, error_msg)
                elif action.capture_output and out:
                    intercept_connection.resolve_code(MessageType.Success, out.stdout)
                else:
                    intercept_connection.resolve_code()
            else:
                # We did not handle it so we ignore it and it will be continued to be processed
                intercept_connection.ignore_code()
    except Exception as e:
        print("Closing connection: ", e)
        traceback.print_exc()
        intercept_connection.close()


def get_actions_from_config():
    actions = []
    filter_filepath = DSF_PLUGINS_DIR / f'{PLUGIN_NAME}/dwc/filters.json'
    if not filter_filepath.is_file():
        return actions

    with open(filter_filepath) as fp:
        json_filter = json.load(fp)
        for action in json_filter:
            if action['code'] in DEFAULT_FILTERS:
                # TODO: See why messages are not displayed in DWC or logs
                sys.stderr.write(f"{action['code']} is a reserved filter and thus it can't be used.")
                continue
            try:
                actions.append(MCodeAction(action))
            except KeyError as e:
                sys.stderr.write(e)
    return actions


if __name__ == "__main__":
    intercept_mcodes(get_actions_from_config())
