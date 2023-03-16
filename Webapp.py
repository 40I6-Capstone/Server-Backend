import asyncio;
import websockets;

class Webapp:
    def __init__(self, local_ip, local_port):
        """
        Binds to the local IP/port to the webapp.
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
        self.websocket = websocket;

        consumer_task = asyncio.create_task(self.getPacket(websocket));
        producer_task = asyncio.create_task(self.sendPacket(websocket));
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        );
        for task in pending:
            task.cancel();
    
    async def getPacket(self, websocket):
        async for message in websocket:
            print(f'!!!!!!\nGot message!! {message}\n');
    
    async def sendPacket(self, websocket):
        while True:
            print(".")
            message = await self.send_message_queue.get();
            print("sending message", message);
            await websocket.send(message);
            self.send_message_queue.task_done();
            print("done sending message");
            print();
    
    async def putMessageInQueue(self, value):
        await self.send_message_queue.put(value);
        print(f'add {value} to queue');
        await asyncio.sleep(0.5);

