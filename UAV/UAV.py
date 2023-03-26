from UAVState import UAVStateListener
import socket;
import threading;
import time;
import cv2;
import numpy as np;
import asyncio;

DEFAULT_RESPONSE_TIMEOUT = 10

class UAV:
    _transport = None;
    _protocol = None;

    class Error(Exception):
        '''
        Exception thrown if anything goes wrong controlling the drone.
        '''
        pass
    class Protocol:
        '''
        UDP protocol for drone control using the Tello SDK.
        The basic flow from the user's point of view is
        SEND command → drone does something → RECEIVE response when it's finished
        Messages are plain ASCII text, eg command `forward 10` → response `ok`
        '''
        def connection_made(self, transport):
            self.pending = []

        def datagram_received(self, data, addr):
            try:
                message = data.decode('ascii')
            except UnicodeDecodeError as e:
                raise UAV.Error(f'DECODE ERROR {e} (data: {data})')
                
            print('RECEIVED', message)
            try:
                sent_message, response = self.pending.pop(0)
   
                if message == 'ok':
                    result = None
                else:
                    response.set_exception(UAV.Error(message))
                    return
                response.set_result((sent_message, result))

            except IndexError:
                raise UAV.Error('NOT WAITING FOR RESPONSE')
            except asyncio.InvalidStateError:
                pass

        def error_received(self, error):
            raise UAV.Error(f'PROTOCOL ERROR {error}')

        def connection_lost(self, error):
            # print('CONNECTION LOST', error)
            for m, response, rp in self.pending:
                response.cancel()
                self.pending.clear()



    def __init__(self, local_ip, local_port, tello_ip="192.168.10.1", tello_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.
        :param local_ip (str): Local WLAN IP address to bind.
        :param local_port (int): Local port to bind.
        :param tello_ip (str): Tello IP.
        :param tello_port (int): Tello port.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        self.local_ip = local_ip;
        self.local_port = local_port;
        self.uav_ip = tello_ip;
        self.uav_port = tello_port;
        self.connected = False;

        self.image_port = 11111;
        # self.uavSem = uavSem;
        self.loop = asyncio.get_running_loop();

        self.sendCommandQueue = asyncio.Queue();
        
        # set up socket for sending commands to tello drone
        # self.socket.bind((local_ip, local_port));

        # start listening for any acks or state updates from the tello drone
        # self.listening_thread = threading.Thread(target=self._listening_thread);
        # self.listening_thread.daemon = True;
        # self.listening_thread.start();
        # asyncio.create_task(sendCommandQueue);

        # self.send_command("command");
        # self.send_command("streamon");

    async def connect(self):
        transport, protocol = await self.loop.create_datagram_endpoint(
            UAV.Protocol, 
            local_addr=(self.local_ip, self.uav_port),
            remote_addr=(self.uav_ip, self.uav_port)
        )
        self._transport = transport;
        self._protocol = protocol;
        
        self.state_listener = UAVStateListener(self.local_ip, self.local_port)
        await self.state_listener.connect(self.loop);
    
        response = await self.send('command');
        response = await self.send('streamon');
        return response;

    async def send(self, message, timeout=DEFAULT_RESPONSE_TIMEOUT):
        '''
        Send a command message and wait for response.

        :param message: The command string
        :param timeout: Time to wait in seconds for a response
        :param response_parser: A function that converts the response into a return value. 
        :return: The response from the drone
        :rtype: str, unless `response_parser` is used.
        '''
        if not self._transport.is_closing():
            print(f'SEND {message}')
            
            self._transport.sendto(message.encode())

            response = self.loop.create_future()
            self._protocol.pending.append((message, response))
            error = None
            try:
                response_message, result = await asyncio.wait_for(response, timeout=timeout)
                if response_message == message:
                    return result
                else:
                    error = UAV.Error('RESPONSE WRONG MESSAGE "{response_message}", expected "{message}" (UDP packet loss detected)')
            except asyncio.TimeoutError:
                error = UAV.Error(f'[{message}] TIMEOUT')
            except UAV.Error as e:
                error = UAV.Error(f'[{message}] ERROR {e}')
    
            # default behaviour
            await self._abort()
            raise error

    async def receiveTask(self, reader: asyncio.StreamReader):
        while (1):
            data = await reader.read();
            print(f'Received: {data.decode()!r}')
    
    async def sendCommandTask(self, writer: asyncio.StreamWriter):
        while (1):
            command  = await self.sendCommandQueue.get();
            writer.write(command.encode("utf-8"));
            await writer.drain();
    
            

    # def _listening_thread(self):
    #     """
    #     Listen to responses from the Tello.
    #     Runs as a thread, sets self.response to whatever the Tello last returned.
    #     """
        
    #     while True:
    #         try:
    #             self.response, ip = self.socket.recvfrom(3000);
    #             match (self.response.decode()):
    #                 case 'ok':
    #                     print("got command ok");
    #                     self.uavSem.release();
    #                 case 'error':
    #                     print("error sending command");
    #                 case other:
    #                     # self.state = json.loads(self.response);
    #                     stateArr = self.response.decode().replace("\\r\\n","").split(';');
    #                     for data in stateArr:
    #                         if(not ":" in data): continue;
    #                         splitData = data.split(":");
    #                         setattr(self.state, splitData[0], splitData[1]);
    #             # if(self.response.decode() == 'ok'): print('ok');
    #             # print(self.response)
    #         except socket.error as err:
    #             print ("Caught exception UGV receive socket.error : %s" % err);
    
    # def send_command(self, command):
    #     self.socket.sendto(command.encode("utf-8"), self.uav_address);
    #     print("send command: %s to %s"%(command, self.uav_address));

    def capture_photo(self):
        cap = cv2.VideoCapture(f'udp://@{self.uav_ip}:{self.image_port}');
        gotFrame = False;
        while(not gotFrame):
            gotFrame, frame = cap.read();
        cap.release();
        return(frame);

    # def close(self):
    #     self.send_command("streamoff");
    #     self.socket.close();

        




