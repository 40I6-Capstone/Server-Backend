import UGV.Node as Node
import UGV.Packet as Packet
import asyncio
import struct


class NodeManager:
    packet_type = {  # dictionary for packet type
        "who_am_i": '0',
        "node_state": '1',
        "path": '2',
        "stop": '3',
        "go": '4',
        "diag_state": '5',
        "esp_status": '6',
        # str.encode(packet_type["node"]) = b'1'
        # str.encode(packet_type["path"]) = b'2'
    }

    def __init__(self, websocket, nodeID):  # take in socket and nodeID as arguments
        self.nodeID = nodeID
        self.websocket = websocket
        self.send_packet_queue = asyncio.Queue()
        self.send_path_semaphore = asyncio.Semaphore()
        self.diag_state = None;
        self.state = None;

    # create get message function
    async def getPacket(self, websocket, updateStateSem: asyncio.Semaphore, updateDiagStateSem: asyncio.Semaphore):
        async for message in websocket:
            packet = struct.unpack('c', message[:1]);
            # TODO receive and determine what type of packet has been received between debug and node state then parse the packet and put it in queue for the server
            match (packet[0].decode()):
                case '5':
                    diag_packet = Packet.diagnostic_state(message)
                    self.diag_state = diag_packet;
                    updateDiagStateSem.release();
                case '1':
                    node_state_packet = Packet.node_state(message)
                    self.state = node_state_packet;
                    updateStateSem.release();
                case '6':
                    if message['data'] == 'ready':
                        self.send_path_semaphore.release()  # adds 1 to the semaphore so that data can be sent to the esp
                    if message['data'] == 'good':
                        continue
                    if message['data'] == 'nope':  # when esp sends nope, we assume is already ready to receive path packet again
                        continue


    async def sendPacket(self, websocket):
        while True:
            message = await self.send_packet_queue.get();
            await websocket.send(message);
            self.send_packet_queue.task_done();
            await asyncio.sleep(0.01);
