#!/usr/bin/env python3

import json

from dsf.commands.basecommands import HttpEndpointType
from dsf.http import HttpEndpointConnection

PLUGIN_NAME = "ExecOnMcode"


async def getCmdList_handler(http_endpoint_connection: HttpEndpointConnection):
    await http_endpoint_connection.read_request()

    # TODO: resolve the path using DSF API
    filter_filepath = "/opt/dsf/sd/sys/ExecOnMcode.json"
    with open(filter_filepath) as fp:
        file_data = json.load(fp)
    json_data = {'data': file_data}

    await http_endpoint_connection.send_response(200, json.dumps(json_data))
    http_endpoint_connection.close()


def custom_http_endpoint(cmd_conn):
    # Setup the endpoint
    endpoint = cmd_conn.add_http_endpoint(HttpEndpointType.GET, PLUGIN_NAME, "getCmdList")
    # Register our handler to reply on requests
    endpoint.set_endpoint_handler(getCmdList_handler)

    return endpoint
