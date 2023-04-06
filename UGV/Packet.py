from enum import Enum
import struct
import time

class State (Enum):
    NODE_IDLE = 0;
    NODE_PATH_LEAVE = 1;
    NODE_PATH_RETURN = 2;
    NODE_DONE = 3;

class Packet:
    def __init__(self, data):
        self.data = data

    # byte sizes for different data types:
    # char - 1
    # short - 2
    # int - 4
    # long - 8
    # long long - 8
    # double - 8 bytes
    # uint64_t - 8 bytes
    # we will make our packet size 42 bytes, this accomodates note State (42 bytes) and pathpoint (41 bytes)
    def packetType(self):
        if self.data[0:1] == b'1':
            return 1
        if self.data[0:1] == b'2':
            return 2


class node_state(Packet):
    def __init__(self, data, timeStart):
        self.data = data
        self.code = None
        self.x = None
        self.y = None
        self.velocity = None
        self.heading = None
        self.ts_ms = (time.time_ns()*1000000)-timeStart
        self.State = None
        self.x_exp = None
        self.y_exp = None
        self.velocity_exp = None
        self.heading_exp = None
        self.convertData()

    def convertData(self):
        data = struct.unpack('cddddhdddd', self.data);
        self.code = data[0].decode() # packet code
        self.x = data[1]  # Estimated x position relative to start (double - 8 bytes)
        self.y = data[2] # Estimated y position relative to start (double - 8 bytes)
        self.velocity = data[3] # current velocity (double - 8 bytes)
        self.heading = data[4]  # heading angle relative to start (double - 8 bytes)
        self.State = State(data[5])  # byte enumeration of node executing state (char - 1 byte)
        self.x_exp = data[6]  # double
        self.y_exp = data[7]  # double
        self.velocity_exp = data[8]  # double
        self.heading_exp = data[9]  # double
    
    def convertToDict(self):
        dict = vars(self);
        try:
            del dict["data"];
            del dict["code"];
            dict["State"] = dict["State"].name;
        except:
            print("data or code doesn't exist or state is not enum");
        return dict;


class diagnostic_state(Packet):
    def __init__(self, data, timeStart):
        self.data = data
        self.code = None
        self.ts_ms = (time.time_ns()*1000000)-timeStart
        self.v_right = None
        self.d_right = None
        self.v_left = None
        self.d_left = None
        self.v_avg = None
        self.d_avg = None
        self.convertData()

    def convertData(self):
        data = struct.unpack('cdddd', self.data)
        self.code = data[0]  # packet code
        self.v_right = data[1]  # double
        self.d_right = data[2]  # double
        self.v_left = data[3]  # double
        self.d_left = data[4]  # double
        self.v_avg = (self.v_right+self.v_left)/2
        self.d_avg = (self.d_right+self.d_left)/2
    
    def convertToDict(self):
        dict = vars(self);
        del dict["data"];
        del dict["code"];
        return dict;


class path_packet(Packet):
    def __init__(self, data):
        self.data = data
        self.code = None
        self.x = None
        self.y = None
        self.convertData()

    def convertData(self):
        self.code = self.data[0]  # packet code
        self.x = self.data[1:9]  # x position for path point (double - 8 bytes)
        self.y = self.data[9:17]  # y position for path point (double - 8 bytes)


#
# class NodeManager:
#     def __init__(self, id, ws):
#         self.id = id
#         self.ws = ws


# one fsm branches between packet codes, sub FSM handles conversation back and forth between
# draw the FSM before coding
