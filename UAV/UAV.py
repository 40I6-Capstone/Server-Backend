from UAV.UAVState import UAVStateListener
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
            self.transport = transport;

        def datagram_received(self, data, addr):
            try:
                message = data.decode('ascii')
            except UnicodeDecodeError as e:
                raise UAV.Error(f'DECODE ERROR {e} (data: {data})')
                
            try:
                sent_message, response = self.pending.pop(0)
                print(message, message[0].isnumeric());
                result = None;
                if message == 'ok':
                    result = None
                elif message[0].isnumeric():
                    result = message;
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
            self.pending = [];

    def __init__(self, local_ip, local_port, main_queue: asyncio.Queue, tello_ip="192.168.10.1", tello_port=8889):
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
        self.main_queue = main_queue;

        self.image_port = 11111;
        self.loop = asyncio.get_running_loop();

        self.sendCommandQueue = asyncio.Queue();

    async def connect(self):
        transport, protocol = await self.loop.create_datagram_endpoint(
            UAV.Protocol, 
            local_addr=(self.local_ip, self.uav_port),
            remote_addr=(self.uav_ip, self.uav_port)
        )
        self._transport = transport;
        self._protocol = protocol;
        
        self.state_listener = UAVStateListener(self.local_ip, self.local_port, self.main_queue)
        await self.state_listener.connect(self.loop);
    
        response = await self.send('command');
        response = await self.send('streamon');

        message = {
            'source': 'UAV',
            'data': {
                'type': 'connected',
            }
        };
        await self.main_queue.put(message);
        asyncio.create_task(self.checkConnection());
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
            print(error);
            return None;
            # default behaviour
            # raise error

    def capture_photo(self):
        cap = cv2.VideoCapture(f'udp://@{self.uav_ip}:{self.image_port}');
        gotFrame = False;
        while(not gotFrame):
            gotFrame, frame = cap.read();
        cap.release();
        return(frame);

    async def checkConnection(self):
        while(1):
            result = await self.send('wifi?');
            if (result == None):
                if(not self._transport == None):
                    self._transport.close();
                    self.state_listener._transport.close();
                self.connected = False;
                message = {
                    'source': 'UAV',
                    'data': {
                        'type': 'disconnected',
                    }
                };
                await self.main_queue.put(message);
                break;
            await asyncio.sleep(5);

            

    # def close(self): 
    #     self.send_command("streamoff");
    #     self.socket.close();

        




