import websockets;
import asyncio;

from NodeManager import NodeManager

host_ports = [];

class UGV:
    def __init__(self, local_ip, local_port):
        """
        Binds to the local IP/port to the UGV.
        :param host_ip (str): Local IP address to bind.
        :param host_base_port (int): Local port to bind.
        """
        print(f'Port {local_port}');
        self.local_address = {"local_ip": local_ip, "local_port": local_port };        
        self.send_message_queue = asyncio.Queue();
        self.websocket = None;


    async def start_network(self):
        async with websockets.serve(self._network_handler, self.local_address["local_ip"], self.local_address["local_port"]):
            await asyncio.Future()  # run forever

    async def _network_handler(self, websocket):
        if(self.websocket != None):
            print ("SOMETHING IS ALREADY CONNECTED");
            return;
        self.id = len(host_ports);
        host_ports.append((self.id, self.local_address["local_port"]));
        print("new websocket", websocket);
        self.websocket = websocket;
        self.nodeManager = NodeManager(websocket, self.id);

        consumer_task = asyncio.create_task(self.nodeManager.getPacket(websocket));
        producer_task = asyncio.create_task(self.nodeManager.sendPacket(websocket, self.send_message_queue));
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        );
        for task in pending:
            task.cancel();
    
    async def putMessageInQueue(self, value):
        await self.send_message_queue.put(value);
        print(f'add {value} to queue');
        await asyncio.sleep(0.5);



