import socket;
import threading;
import websockets;
import asyncio;

host_ports = [];

class UGV:
    def __init__(self, local_ip, local_port):
        """
        Binds to the local IP/port to the UGV.
        :param host_ip (str): Local IP address to bind.
        :param host_base_port (int): Local port to bind.
        """
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

        self.local_address = {"local_ip": local_ip, "local_port": local_port };        
        self.send_message_queue = asyncio.Queue();
        self.websocket = None;

        # self.socket.bind(local_address);
        # self.socket.listen(1);
        # print("listening");
        # self.client, self.client_address = self.socket.accept();
        # print("UGV with address %s is connected to the server on %s"%(self.client_address, local_address));

        # self.id = len(host_ports);
        # host_ports.append((self.id, local_port));

        # self.listening_thread = threading.Thread(target=self._networking_thread);
        # self.listening_thread.daemon = True;
        # self.listening_thread.start();

    async def start_network(self):
        async with websockets.serve(self._network_handler, self.local_address["local_ip"], self.local_address["local_port"]):
            await asyncio.Future()  # run forever

    async def _network_handler(self, websocket):
        self.id = len(host_ports);
        host_ports.append((self.id, self.local_address["local_port"]));
        print("new websocket", websocket);
        self.websocket = websocket;

        consumer_task = asyncio.create_task(self._get_message_handler(websocket))
        producer_task = asyncio.create_task(self._send_message_handler(websocket))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
    async def _send_message_handler(self, websocket):
        while True:
            print(".")
            message = await self.send_message_queue.get();
            print("sending message", message);
            await websocket.send(message);
            self.send_message_queue.task_done();
            print("done sending message");
            print();
    
    async def _get_message_handler(self, websocket):
        async for message in websocket:
            print(f'!!!!!!\nGot message!! {message}\n');
        print("done consumer");

    async def putMessageInQueue(self, value):
        await self.send_message_queue.put(value);
        print(f'add {value} to queue');
        await asyncio.sleep(0.5);
    # def _networking_thread(self):
    #     while True:
    #         try:
    #             self.response = self.client.recv(3000);
    #             if(self.response):
    #                 # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
    #                 response = '''HTTP/1.1 101 Switching Protocols
    #                 Upgrade: websocket
    #                 Connection: Upgrade
    #                 Sec-WebSocket-Protocol:'''
    #                 # sending all this stuff
    #                 self.client.send((response).encode())
                    
    #                 print("got message", self.response.decode());
    #             if(len(self.send_message_queue)>0):
    #                 print ("send message", self.send_message_queue[-1]);
    #                 self.client.send(self.send_message_queue.pop().encode())
    #         except socket.error as err:
    #             print ("Caught exception UGV receive socket.error : %s" % err);


