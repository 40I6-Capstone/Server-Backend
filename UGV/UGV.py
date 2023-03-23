import websockets;
import asyncio;
import numpy as np;

from UGV.NodeManager import NodeManager

host_ports = [];

class UGV:
    def __init__(self, local_ip, local_port, mainQueue: asyncio.Queue):
        """
        Binds to the local IP/port to the UGV.
        :param host_ip (str): Local IP address to bind.
        :param host_base_port (int): Local port to bind.
        """
        print(f'Port {local_port}');
        self.local_address = {"local_ip": local_ip, "local_port": local_port };        
        self.send_message_queue = asyncio.Queue();
        self.websocket = None;
        self.paths = [];
        self.mainQueue = mainQueue;


    async def start_network(self):
        async with websockets.serve(self._network_handler, self.local_address["local_ip"], self.local_address["local_port"]):
            await asyncio.Future()  # run forever

    async def _network_handler(self, websocket):
        if(self.websocket != None):
            print ("SOMETHING IS ALREADY CONNECTED");
            return;
        self.id = len(host_ports);
        host_ports.append((self.id, self.local_address["local_port"]));
        await self.mainQueue.put({
            "source": "ugv",
            "data": {
                "type": "ugvAdded",
                "id": self.id,
            }
        });
        self.websocket = websocket;
        self.nodeManager = NodeManager(websocket, self.id);

        consumer_task = asyncio.create_task(self.nodeManager.getPacket(websocket));
        producer_task = asyncio.create_task(self.nodeManager.sendPacket(websocket));
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        );
        for task in pending:
            task.cancel();
    
    def setPaths(self, paths):
        self.paths = paths;
    async def sendNewPath(self):
        path = self.paths.pop(0).points;
        message = {
            "code": 2,
            "data": np.array2string(path),
        };
        self.send_message_queue(message);
    
    async def putMessageInQueue(self, value):
        await self.nodeManager.send_packet_queue.put(value);
        print(f'add {value} to queue');
        await asyncio.sleep(0.5);



