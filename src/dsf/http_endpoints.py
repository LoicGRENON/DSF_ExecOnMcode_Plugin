import json

from dsf.connections import CommandConnection
from dsf.http import HttpEndpointConnection, HttpEndpointType

PLUGIN_NAME = "ExecOnMcode"
filter_filepath = ""


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
    request = await http_endpoint_connection.read_request()
    # Write the commands list to the JSON file
    with open(filter_filepath, 'w') as fp:
        # TODO: Make sure the command code is Mxxx before to save it / Sanitize the data
        fp.write(json.dumps(json.loads(request.body), indent=4))

    response_data = {'success': True}
    await http_endpoint_connection.send_response(200, json.dumps(response_data))
    http_endpoint_connection.close()

    cmd_conn = CommandConnection()
    cmd_conn.connect()
    try:
        # Send M1200 to update interception filters 
        cmd_conn.perform_simple_code('M1200')
    finally:
        cmd_conn.close()


def custom_http_endpoints(cmd_conn):
    endpoints = []

    # Use DSF API to get the physical path to the configuration file
    res = cmd_conn.resolve_path(f"0:/sys/{PLUGIN_NAME}/{PLUGIN_NAME}.json")
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
