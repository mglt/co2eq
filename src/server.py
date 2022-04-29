import asyncio

import websockets
import base64
import os
from co2eq.conf import CONF

# create handler for each connection

output_file_path = CONF['OUTPUT_DIR']

async def handler(websocket, path):

    data = await websocket.recv()

    print(f"Data recieved as:  {data}!")
    file_path = "ICANN555/co2eq-mode_flight_distance-cluster_key_flight_segment_number-cluster_nbr_15-co2eq_myclimate_goclimate.svg"
    graph_path = os.path.join(output_file_path,file_path)
    with open(graph_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    await websocket.send(encoded_string.decode('utf8'))


 

start_server = websockets.serve(handler, "", os.environ.get('PORT', 8000))

 

asyncio.get_event_loop().run_until_complete(start_server)

asyncio.get_event_loop().run_forever()