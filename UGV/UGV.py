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
        self.updateStateSem = asyncio.Semaphore();
        self.updateDiagStateSem = asyncio.Semaphore();
        self.websocket = None;
        self.paths = [];
        self.stateHistory = [];
        self.diagStateHistory = [];
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

        getPacket_task = asyncio.create_task(self.nodeManager.getPacket(websocket, self.updateStateSem, self.updateDiagStateSem));
        sendPacket_task = asyncio.create_task(self.nodeManager.sendPacket(websocket));
        updateState_task = asyncio.create_task(self.updateState());
        updateDiagState_task = asyncio.create_task(self.updateDiagState());
        done, pending = await asyncio.wait(
            [getPacket_task, sendPacket_task, updateState_task, updateDiagState_task],
            return_when=asyncio.FIRST_COMPLETED,
        );
        for task in pending:
            task.cancel();
    
    async def updateState(self):
        while(1):
            await self.updateStateSem.acquire();
            self.stateHistory.append(self.nodeManager.state);
            message = {
                "source": "ugv",
                "data": {
                    "type": "state",
                    "id": self.id,
                    "data": self.nodeManager.state.convertToDict(),
                }
            };
            await self.mainQueue.put(message);
    
    async def updateDiagState(self):
        while(1):
            await self.updateDiagStateSem.acquire();
            self.diagStateHistory.append(self.nodeManager.diag_state);
            message = {
                "source": "ugv",
                "data": {
                    "type": "diagState",
                    "id": self.id,
                    "data": self.nodeManager.diag_state.convertToDict(),
                }
            };
            await self.mainQueue.put(message);

    def setPaths(self, paths):
        self.paths = paths;
        
    async def sendNewPath(self):
        path = self.paths.pop(0).points;
        message = {
            "code": 2,
            "data": np.array2string(path),
        };
        await self.nodeManager.send_packet_queue(message);
    
    async def putMessageInQueue(self, value):
        await self.nodeManager.send_packet_queue.put(value);
        print(f'add {value} to queue');
        await asyncio.sleep(0.5);

    async def stop(self):
        await self.nodeManager.send_packet_queue.put(3)

    async def go(self):
        await self.nodeManager.send_packet_queue.put(4)



