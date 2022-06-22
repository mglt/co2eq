import asyncio
import websockets
import base64
import os
#from conf import CONF
#from plot_meeting import plot_meeting
import json
import shutil
from threading import Thread
import signal
import co2eq.conf
import co2eq.meeting 

## reading configuration from .env
CONF = co2eq.conf.Conf( ).CONF
output_file_path = CONF['OUTPUT_DIR']

async def handler(websocket, path):

    data = await websocket.recv()

    data_dict = json.loads(data)

    print(data_dict)

    async def fileWatch():
        sent_files = []
        while True:
            if os.path.isdir(os.path.join(output_file_path, data_dict['name'])):
                for file_name in os.listdir(os.path.join(output_file_path, data_dict['name'])):
                    if file_name.endswith('.svg'):
                        if file_name not in sent_files:
                            sent_files.append(file_name)
                            graph_path = os.path.join(output_file_path, data_dict['name'], file_name)
                            with open(graph_path, "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read())
                            await websocket.send(encoded_string.decode('utf8'))
                    else:
                        continue
            await asyncio.sleep(5)

    def runFileWatch():
        asyncio.run(fileWatch())
    
    _thread = Thread(target=runFileWatch)
    _thread.start()

    ## ploting the data
    ## The server plots the data for a single meeting. One motivation 
    ## is that MeetingList has a more formal structure to define 
    ## the meeting name, location, in a JSON object while Meeting 
    ## uses these information as arguments.
    ## We could have used the Meeting object as well. 
    meeting_list = co2eq.meeting.MeetingList( name=data['name'], conf=CONF, meeting_list=[ data ] )
    meeting_list.plot_all()
    await asyncio.sleep(5)

    delete_folder(os.path.join(output_file_path, data_dict['name']))

def delete_folder(folder_name):
    try:
        shutil.rmtree(folder_name)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

async def start_server(stop):
    async with websockets.serve(handler, "", os.environ.get('PORT', 8000)):
        await stop

loop = asyncio.get_event_loop()
stop = loop.create_future()
loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

loop.run_until_complete(start_server(stop))

loop.run_forever()
