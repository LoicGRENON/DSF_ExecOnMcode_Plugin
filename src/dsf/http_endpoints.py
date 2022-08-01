#!/usr/bin/env python3

import json

from dsf.commands.basecommands import HttpEndpointType
from dsf.http import HttpEndpointConnection

PLUGIN_NAME = "ExecOnMcode"
filter_filepath = ""
cmd_conn = None


async def getCmdList_handler(http_endpoint_connection: HttpEndpointConnection):
    await http_endpoint_connection.read_request()

    try:
        with open(filter_filepath) as fp:
            file_data = json.load(fp)
    except FileNotFoundError:
        file_data = []
    except json.decoder.JSONDecodeError:
        file_data = []

    json_data = {'data': file_data}
    await http_endpoint_connection.send_response(200, json.dumps(json_data))
    http_endpoint_connection.close()


async def saveCmdList_handler(http_endpoint_connection: HttpEndpointConnection):
    response = await http_endpoint_connection.read_request()
    print(response.body)

    with open(filter_filepath, 'w') as fp:
        # TODO: Make sure the command code is Mxxx
        fp.write(json.dumps(json.loads(response.body), indent=4))

    response_data = {'success': True}
    await http_endpoint_connection.send_response(200, json.dumps(response_data))
    http_endpoint_connection.close()


def custom_http_endpoints(cmd_conn):
    endpoints = []

    # Use DSF API to get the physical path to the configuration file
    res = cmd_conn.resolve_path(f"0:/sys/{PLUGIN_NAME}.json")
    global filter_filepath
    filter_filepath = res.result if res else None

    # Setup the endpoint and register the handler to reply on GET requests to read the commands list
    endpoint = cmd_conn.add_http_endpoint(HttpEndpointType.GET, PLUGIN_NAME, "getCmdList")
    endpoint.set_endpoint_handler(getCmdList_handler)
    endpoints.append(endpoint)

    # Setup the endpoint and register the handler to reply on POST requests to save the commands list
    endpoint = cmd_conn.add_http_endpoint(HttpEndpointType.POST, PLUGIN_NAME, "saveCmdList")
    endpoint.set_endpoint_handler(saveCmdList_handler)
    endpoints.append(endpoint)

    return endpoints
