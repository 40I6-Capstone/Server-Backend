import websockets
# import socket
import asyncio
# import warnings
import struct
import Packet
import Node
import time

PORT = 1234
#url = "192.168.244.243"
# url = "localhost"
url = "192.168.244.243"

# # Example path packet data
# x = b'15.10100'
# y = b'34.35000'
# ts_ms = b'10506789'
# v = b'2.300000'
# heading = b'19.12345'
# path = b'2' + x + y + ts_ms + v + heading

# Example path packet data
x = '15.10100'
y = '34.35000'
v = '2.300000'
heading = '19.12345'
ts_ms = '10506789'

path = x + y + ts_ms + v + heading
path2 = '2' + x + y +  v + heading + ts_ms

async def start_network():
    async with websockets.serve(handler, url, PORT):
        # print(type(path))
        # print(path)
        await asyncio.Future()  # run forever


# create handler for each connection
async def handler(websocket):
    while(1):
        data = await websocket.recv()
        print(data)
        # reply = f"Data recieved as:  {data}!"
        await websocket.send(path2.encode())
        # await websocket.send(path2)
        await asyncio.sleep(5)



# start_server = websockets.serve(handler, url, PORT)
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
asyncio.run(start_network())
