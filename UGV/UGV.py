import websockets;
import asyncio;
import numpy as np;

from UGV.NodeManager import NodeManager
from UGV.Packet import State

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
        self.pathIndexes = [];
        self.stateHistory = [];
        self.diagStateHistory = [];
        self.mainQueue = mainQueue;
    
    def getNodeState(self):
        state = self.getStateHistory[-1].convertToDict();
        if(state["State"] == State.NODE_IDLE and len(self.pathIndexes) == 0):
            state["State"] = State.NODE_DONE;
        return state;
    


    async def start_network(self):
        async with websockets.serve(self._network_handler, self.local_address["local_ip"], self.local_address["local_port"]):
            await asyncio.Future()  # run forever

    async def _network_handler(self, websocket):
        if(self.websocket != None):
            # websocket.close();
            print ("SOMETHING IS ALREADY CONNECTED");
            return;
        self.id = len(host_ports);
        host_ports.append((self.id, self.local_address["local_port"]));
        print("UGV", self.id);
        await self.mainQueue.put({
            "source": "ugv",
            "data": {
                "type": "connected",
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
        await self.updateStateSem.acquire();
        while(1):
            print(self.updateStateSem._value);
            await self.updateStateSem.acquire();
            self.stateHistory.append(self.nodeManager.state);
            message = {
                "source": "ugv",
                "data": {
                    "type": "state",
                    "id": self.id,
                    "data": self.getNodeState(),
                }
            };
            await self.mainQueue.put(message);
    
    async def updateDiagState(self):
        await self.updateDiagStateSem.acquire();
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

    def setPaths(self, pathsIndexes):
        self.pathIndexes = pathsIndexes;
        
    async def sendNewPath(self, paths):
        pathPoints = paths[self.pathIndexes.pop(0)].points;
        for point in pathPoints: 
            await self.nodeManager.send_packet_queue.put(f'2{point[0]}{point[1]}');
            
    
    async def putMessageInQueue(self, value):
        await self.nodeManager.send_packet_queue.put(value);
        await asyncio.sleep(0.1);
    
    async def getState(self): 
        await asyncio.sleep(15);
        while (1):
            if (len(self.pathIndexes) == 0): continue;
            await self.nodeManager.send_packet_queue.put("1");
            await asyncio.sleep(1);

    async def stop(self):
        await self.nodeManager.send_packet_queue.put("3")

    async def go(self):
        await self.nodeManager.send_packet_queue.put("4")



