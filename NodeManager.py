class NodeManager:

    packet_type = {  # dictionary for packet type
        "who_am_i": '0',
        "node": '1',
        "path": '2'
        # str.encode(packet_type["node"]) = b'1'
        # str.encode(packet_type["path"]) = b'2'
    }

    def __init__(self, websocket, nodeID):  # take in socket and nodeID as arguments
        self.nodeID = nodeID
        self.websocket = websocket;
    
    #create get message function 
    async def getPacket(self, websocket):
        async for message in websocket:
            #TODO complete stuff to do with the packet
            break;

    async def sendPacket(self, websocket, queue):
        while True:
            message = await queue.get();
            #TODO complete tasks with what you get from queue
            await websocket.send(message);
            queue.task_done();

