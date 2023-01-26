# Author: Julian Morrone (jmorrone1499@gmail.com)
# Version: 1.2
# Date: December 2, 2022

#!usr/bin/python
import _thread
import socket
import sys
import asyncio
import Packet  # Packet class
import Node

global packet_type
global state  # make state a global variable so that it can be modified in class methods
global mode
mode = 'testing'


class node_manager:

    packet_type = {  # dictionary for packet type
        "who_am_i": '0',
        "node": '1',
        "path": '2'
        # str.encode(packet_type["node"]) = b'1'
        # str.encode(packet_type["path"]) = b'2'
    }

    if mode == 'testing':
        def __init__(self, nodeID):  # take in socket and nodeID as arguments
            self.nodeID = nodeID
            self.new_node()

    if mode == 'production':
        def __init__(self, conn, addr, nodeID):  # take in socket and nodeID as arguments
            self.conn = conn  # new socket object usable to send and receive data on the connection
            self.addr = addr  # the address bound to the socket on the other end of the connection
            self.nodeID = nodeID
            self.new_node()

    async def send_path(path_packet, Node):
        Node.conn.sendall(path_packet.data__)
        global state
        state = 'SEND_PATH_PACKET'

    async def request_state(self):
        global state
        state = 'REQUEST_NODE_STATE'


    def new_node(self):

        # Example path packet data
        x = b'15.10100'
        y = b'34.35000'
        ts_ms = b'10506789'
        v = b'2.300000'
        heading = b'19.12345'
        path = x + y + ts_ms + v + heading

        host = '192.168.0.54'
        port = 7890
        if mode == 'testing':
            tot_socket = 1  # total number of sockets that we are connecting to
            list_sock = []
            node_list = []
            node_index = 0

        global state
        state = 'REGISTER_CLIENT'

        while 1:
            match state:
                case 'REGISTER_CLIENT':
                    if mode == 'testing':  # testing or production mode
                        print('********  REGISTER_CLIENT STATE  ********')
                        for i in range(tot_socket):
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            s.bind((host, port + i))
                            s.listen(10)
                            list_sock.append(s)
                            print("[*] Server listening on %s %d" % (host, (port + i)))
                        while len(node_list) < tot_socket:
                            for j in range(len(list_sock)):
                                conn, addr = list_sock[j].accept()
                                print('[*] Connected with ' + addr[0] + ':' + str(addr[1]))
                                node = Node.Node(conn, addr, 0, 0, 0, 0, 0, 0)
                                # node.conn = conn
                                # node.address = addr
                                node_list.append(node)
                                # _thread.start_new_thread(clientthread, (conn,))
                    if mode == 'production':
                        # TODO at this point Aron would have established the socket connection for you, and then passed it in alongside an ID
                        # this state just needs to send that ID back to the node and setup any callbacks if youre doing asynch stuff <-- make the decision about this soon
                        # dont forget to send back the ID that this object was created with
                        node = Node.Node(self.conn, self.addr, self.ID, 0, 0, 0, 0, 0,0)  # TODO - change ID to be the value passed in from Aron here
                        node.conn.sendall(self.ID)  # send back ID to the node

                    state = 'IDLE'

                case 'IDLE':  # wait for function call or a request from the network
                    if mode == 'testing':
                        print('********  IDLE STATE  ********')
                        selection = int(input(
                            'Enter 1 to request node state, 2 to send a path packet, 3 to check for a node state update: '))
                        if selection == 1:
                            state = 'REQUEST_NODE_STATE'
                        elif selection == 2:
                            state = 'SEND_PATH_PACKET'
                        elif selection == 3:
                            for i in range(len(node_list)):  # check all nodes to see if they sent data
                                received_data = node_list[i].conn.recv(4)
                                if received_data:
                                    node_index = i
                                    if received_data == str.encode(packet_type["node"]):  # checks if we are receiving a node state packet, this can be changed to a 1 later to save data
                                        state = 'NODESTATE_RECEIVE'
                                    elif received_data == str.encode(packet_type["path"]):  # 2 = path packet
                                        state = 'SEND_PATH_PACKET'
                                    break
                        else:
                            print('Invalid Selection')
                    if mode == 'production':
                        # TODO - wait for function call from Aron or a request from the network
                        # in the IDLE state the parent script might ask this class to do something instead of just wait for something over the network
                        # to handle this, a busy wait in the IDLE state is okay but you should create methods that will switch the system state
                        # eg. sendPath() (see fsm) that Aron can call and pass an array of path points in (each to be 1 packet), and then the FSM state switches to the approrpriate state and sends the data accordingly
                        # feel free to talk to me about this
                        # use a while loop to check condition to stay busy
                        while 1:
                            await asyncio.sleep(1)
                            if state != 'IDLE':  # stay in idle until another method changes the state of the FSM
                                break
                        # state = 'IDLE'  # Loop in idle for now but this needs to be changed

                case 'REQUEST_NODE_STATE':
                    if mode == 'testing':
                        print('********  REQUEST_NODE_STATE STATE  ********')
                        node_list[node_index].conn.send(str.encode(packet_type["node"]))
                    if mode == 'production':
                        node.conn.send(str.encode(packet_type["node"]))
                    state = 'NODESTATE_RECEIVE'

                case 'NODESTATE_RECEIVE':  # wait for response from node, once received, parse the data, and update internal current state
                    if mode == 'testing':
                        print('********  NODESTATE_RECEIVE STATE  ********')
                    buffer = b''
                    node_state_packet = Packet.node_state(
                        buffer)  # create packet beforehand so that we can use its size in the while
                    while len(
                            buffer) < node_state_packet.packet_size__:  # wait for the buffer to fill with packet data
                        data = node_list[node_index].conn.recv(
                            node_state_packet.packet_size__)  # packet size of 42 bytes for state
                        buffer += data
                        print(buffer)
                    node_state_packet.data = buffer
                    node_state_packet.parseData()  # parse the received data
                    if mode == 'testing':
                        node_list[node_index].updateState(node_state_packet)
                        print('[*] received and parsed packet ')
                    if mode == 'production':
                        node.updateState(node_state_packet)
                    state = 'IDLE'

                case 'SEND_PATH_PACKET':  # parse received data and update internal current state
                    if mode == 'testing':
                        print('********  SEND_PATH_PACKET STATE  ********')
                        node_list[node_index].conn.sendall(str.encode(packet_type["path"]))  # 2 = path packet
                    if mode == 'production':
                        node.conn.sendall(str.encode(packet_type["path"]))  # 2 = path packet
                    state = 'SENDPATH_AWAIT_REPLY'

                case 'SENDPATH_AWAIT_REPLY':  # wait for ready signal from node
                    if mode == 'testing':
                        print('********  SENDPATH_AWAIT_REPLY STATE  ********')
                        status = node_list[node_index].conn.recv(node.status_size)
                    if mode == 'production':
                        status = node.conn.recv(node.status_size)
                    if status == b'r':  # r for ready
                        state = 'SENDPATH_SEND_STREAM'

                case 'SENDPATH_SEND_STREAM':  # SEND STREAM OF BYTES FOR PATH
                    if mode == 'testing':
                        print('********  SENDPATH_SEND_STREAM STATE  ********')
                    # TODO: path_packet needs to be filled with data received from openCV and path planning algorithm, for now it is left empty
                    path_packet = Packet.path_packet(0, 0, 0, 0, 0, 0)
                    path_packet.data = path
                    if mode == 'testing':
                        node_list[node_index].conn.sendall(path_packet.data)
                    if mode == 'production':
                        node.conn.sendall(path_packet.data)
                    state = 'SENDPATH_AWAIT_CHECK'

                case 'SENDPATH_AWAIT_CHECK':  # wait for packet received from node
                    if mode == 'testing':
                        print('********  SENDPATH_AWAIT_CHECK STATE  ********')
                        status = node_list[node_index].conn.recv(node.status_size)
                    if mode == 'production':
                        status = node.conn.recv(node.status_size)
                    if status == b'g':  # g for good
                        state = 'IDLE'
                    elif status == b'n':  # n for no / nope
                        print('path packet not received properly, trying again')
                        state = 'SENDPATH_AWAIT_REPLY'
                    else:
                        raise Exception("error encountered in sending path")


node_1 = node_manager(1)
