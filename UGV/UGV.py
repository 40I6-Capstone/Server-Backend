import websockets;
import asyncio;
import struct
import numpy as np;
import math;

from UGV.NodeManager import NodeManager
from UGV.Packet import State

host_ports = [];
ugvInCritRad = None;



class UGV:
    crit_rad = 0;
    inCritRad = True;
    isDiag = False;
    id = -1;
    def __init__(self, local_ip, local_port, mainQueue: asyncio.Queue):
        """
        Binds to the local IP/port to the UGV.
        :param host_ip (str): Local IP address to bind.
        :param host_base_port (int): Local port to bind.
        """
        print(f'Port {local_port}');
        self.local_address = {"local_ip": local_ip, "local_port": local_port};
        self.updateStateSem = asyncio.Semaphore();
        self.updateDiagStateSem = asyncio.Semaphore();
        self.websocket = None;
        self.pathIndexes = [];
        self.stateHistory = [];
        self.diagStateHistory = [];
        self.mainQueue = mainQueue;
        self.startStatePoll = False;
        self.currentPathIndex = None;

    def getNodeState(self):
        state = self.stateHistory[-1].convertToDict();
        if (state["State"] == State.NODE_IDLE.name and len(self.pathIndexes) == 0):
            state["State"] = State.NODE_DONE.name;
        return state;

    async def start_network(self):
        async with websockets.serve(self._network_handler, self.local_address["local_ip"], self.local_address["local_port"]):
            await asyncio.Future()  # run forever

    async def _network_handler(self, websocket):
        if (self.websocket != None):
            # websocket.close();
            print("SOMETHING IS ALREADY CONNECTED");
            return;
        self.id = len(host_ports);
        print('ugv', self.id)
        host_ports.append((self.id, self.local_address["local_port"]));
        await self.mainQueue.put({
            "source": "ugv",
            "data": {
                "type": "connected",
                "id": self.id,
                "port": self.local_address["local_port"],
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
        while (1):
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
            if(self.isDiag): continue;
            if(len(self.stateHistory) > 1) :
                if(self.stateHistory[-2].State == State.NODE_PATH_LEAVE.name and self.nodeManager.state.State == State.NODE_PATH_RETURN.name):
                    message = {
                        "source": "ugv",
                        "data": {
                            "type": "placeBoom",
                            "pathIndex": self.currentPathIndex,
                            "ugvId": self.id,
                        }
                    }
                    await self.mainQueue.put(message);
                elif(self.stateHistory[-2].State == State.NODE_PATH_RETURN.name and (self.nodeManager.state.State == State.NODE_IDLE.name or self.nodeManager.state.State == State.NODE_DONE.name)):
                    message = {
                        "source": "ugv",
                        "data": {
                            "type": "finishPath",
                            "pathIndex": self.currentPathIndex,
                            "ugvId": self.id,
                        }
                    }
                    await self.mainQueue.put(message);

            # if ugv is in crit rad
            if(not self.inCritRad):     
                if(math.sqrt(self.nodeManager.state.x*self.nodeManager.state.x +  self.nodeManager.state.y*self.nodeManager.state.y) <= self.crit_rad):
                    self.inCritRad = True;
                    message = {
                        "source": "ugv",
                        "data": {
                            "type": "enterCritRad",
                            "id": self.id,
                        }
                    }
                    await self.mainQueue.put(message);
            else:
                if(math.sqrt(self.nodeManager.state.x*self.nodeManager.state.x +  self.nodeManager.state.y*self.nodeManager.state.y) > self.crit_rad):
                    self.inCritRad = False;
                    message = {
                        "source": "ugv",
                        "data": {
                            "type": "leaveCritRad",
                            "id": self.id,
                        }
                    }

                    await self.mainQueue.put(message);

    async def updateDiagState(self):
        await self.updateDiagStateSem.acquire();
        while (1):
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

    def setCritRad(self, crit_rad):
        self.crit_rad = crit_rad;
    
    def setPaths(self, pathsIndexes):
        self.pathIndexes = pathsIndexes;

    async def sendNewPath(self, paths):
        self.isDiag = False;
        if(len(self.pathIndexes) == 0): return;
        self.currentPathIndex = self.pathIndexes.pop(0);
        pathPoints = paths[self.currentPathIndex].points;
        for point in pathPoints:
            await self.nodeManager.send_packet_queue.put(struct.pack("cdd", b'2', point[0], point[1]));
        await self.go();
        if(not self.startStatePoll):
            self.startStatePoll = True;
            asyncio.create_task(self.getState());

    async def sendDefinedPath(self, path):
        self.isDiag = True;
        path = np.array(path);
        for point in path:
            await self.nodeManager.send_packet_queue.put(struct.pack("cdd", b'2', point[0], point[1]));
        await self.go();
        if(not self.startStatePoll):
            self.startStatePoll = True;
            asyncio.create_task(self.getState());
    
    async def getState(self):
        while (1):
            # if (len(self.pathIndexes) == 0): continue;
            if(len(self.stateHistory) > 0 and self.stateHistory[-1].State == State.NODE_IDLE and len(self.pathIndexes) == 0): break;
            await self.nodeManager.send_packet_queue.put(b'1');
            await asyncio.sleep(1);

    async def stop(self):
        await self.nodeManager.send_packet_queue.put(b'3')

    async def go(self):
        await self.nodeManager.send_packet_queue.put(b'4')
