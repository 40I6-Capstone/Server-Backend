import asyncio;
import websockets;
import json

class Webapp:
    def __init__(self, local_ip, local_port, mainQueue: asyncio.Queue):
        """
        Binds to the local IP/port to the webapp.
        :param host_ip (str): Local IP address to bind.
        :param host_base_port (int): Local port to bind.
        """
        self.local_address = {"local_ip": local_ip, "local_port": local_port };        
        self.send_message_queue = asyncio.Queue();
        self.websocket = None;
        self.mainQueue = mainQueue;
    
    async def start_network(self):
        async with websockets.serve(self._network_handler, self.local_address["local_ip"], self.local_address["local_port"]):
            await asyncio.Future()  # run forever

    async def _network_handler(self, websocket):
        self.websocket = websocket;
        await self.setupTestTask();

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
            data = json.loads(message);
            data = {
                "source": "webapp",
                "data": data
            }
            await self.mainQueue.put(data);
            # if(data["type"] == "start"):
            #     asyncio.create_task(self.testTask());

    
    async def sendPacket(self, websocket):
        while True:
            message = await self.send_message_queue.get();
            # print("sending message", message);
            await websocket.send(message);
            self.send_message_queue.task_done();
    
    async def putMessageInQueue(self, value):
        await self.send_message_queue.put(value);
        await asyncio.sleep(0.5);

    async def setupTestTask(self): 
        message = {
            'source': 'ugv',
            'data': {
                'type': 'connected',
                'id': 0,
            }
        };

        await self.mainQueue.put(message);
        

    async def testTask(self): 
        vHeadActFile = open("../UGVDashboard/velocity_heading_actual.csv", "r");
        vHeadExpFile = open("../UGVDashboard/velocity_heading_expected.csv", "r");
        posActFile = open("../UGVDashboard/position_actual.csv", "r");
        posExpFile = open("../UGVDashboard/position_expected.csv", "r");
        while (1):
            vHAct = vHeadActFile.readline();
            vHAct = vHAct.split(',');
            vHExp = vHeadExpFile.readline();
            vHExp = vHExp.split(',');
            posAct = posActFile.readline();
            posAct = posAct.split(',');
            posExp = posExpFile.readline();
            posExp = posExp.split(',');
            if(len(vHAct)>0):
                message = {
                    "type": "ugvData",
                    "data": {
                        "id": 0,
                        "data": {
                            "ts_ms": vHAct[0],
                            "x": posAct[1],
                            "y": posAct[2],
                            "velocity": vHAct[1],
                            "heading": vHAct[2],
                            "x_exp": posExp[1],
                            "y_exp": posExp[2],
                            "velocity_exp": vHExp[1],
                            "heading_exp": vHExp[2]
                        }
                    }
                };
                await self.putMessageInQueue(json.dumps(message));
            await asyncio.sleep(1);
            
    

