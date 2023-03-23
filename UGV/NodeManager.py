import UGV.Node as Node
import UGV.Packet as Packet
import asyncio


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

    # create get message function
    async def getPacket(self, websocket):
        async for message in websocket:
            # TODO receive and determine what type of packet has been received between debug and node state then parse the packet and put it in queue for the server
            packet = Packet(message)
            if packet.data[0] == 5:  # Diagnostic packet
                diag_packet = Packet.diagnostic_state(message)
                diag_packet.convertData()
                add_msg = asyncio.create_task(self.send_packet_queue.putMessageInQueue(diag_packet))
                await add_msg;
            elif packet.data[0] == 1:  # Node state packet
                node_state_packet = Packet.node_state(message)
                node_state_packet.convertData()
                add_msg = asyncio.create_task(self.send_packet_queue.putMessageInQueue(node_state_packet))
                await add_msg;
            elif packet.data[0] == '6':  # ESP status packet
                if message['data'] == 'ready':
                    self.send_path_semaphore.release()  # adds 1 to the semaphore so that data can be sent to the esp
                if message['data'] == 'good':
                    continue
                if message['data'] == 'nope':  # when esp sends nope, we assume is already ready to receive path packet again
                    continue

    async def sendPacket(self, websocket):
        while True:
            message = await self.send_packet_queue.get();
            # TODO complete tasks with what you get from queue
            print("send message");
            match message.code:  # everything in send packet queue is a packet so it will have a code method
                case 1:  # request Node state
                    await websocket.send(message.code.encode())  # send node state packet code to request node state packet

                case 2:  # send a new Path packet
                    await websocket.send(message.code.encode())  # send path code to the ESP
                    self.send_path_semaphore.acquire()  # semaphore starts at 0 so this code waits until the ESP is ready to read the data from the message
                    await websocket.send(message.data.encode())  # send path packet data to ESP

                case 3:  # STOP
                    await websocket.send(message.code.encode())  # send stop code to ESP

                case 4:  # GO
                    await websocket.send(message.code.encode())  # send go code to ESP

                case 5:  # request diagnostic state packet
                    await websocket.send(message.code.encode())  # send diag packet code to request diag packet

                case other:
                    print("This packet should not be in the send packet queue")

            await websocket.send(message);
            self.send_packet_queue.task_done();