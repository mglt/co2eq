import asyncio

import websockets
import base64
import os
from conf import CONF
from plot_meeting import plot_meeting
import json

output_file_path = CONF['OUTPUT_DIR']

async def handler(websocket, path):

    data = await websocket.recv()

    data_dict = json.loads(data)

    print(data_dict)

    plot_meeting(data_dict)

    for file_name in os.listdir(os.path.join(output_file_path, data_dict['name'])):
        if file_name.endswith('.svg'):
            graph_path = os.path.join(output_file_path, data_dict['name'], file_name)
            with open(graph_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            await websocket.send(encoded_string.decode('utf8'))
        else:
            continue

start_server = websockets.serve(handler, "", os.environ.get('PORT', 8000))

asyncio.get_event_loop().run_until_complete(start_server)

asyncio.get_event_loop().run_forever()