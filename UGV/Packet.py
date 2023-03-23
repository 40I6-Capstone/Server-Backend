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
    def __init__(self, data, code, x, y, velocity, heading, ts_ms, State, x_exp, y_exp, velocity_exp, heading_exp):
        self.data = data
        self.code = code
        self.x = x
        self.y = y
        self.velocity = velocity
        self.heading = heading
        self.ts_ms = ts_ms
        self.State = State
        self.x_exp = x_exp
        self.y_exp = y_exp
        self.velocity_exp = velocity_exp
        self.heading_exp = heading_exp
        self.convertData()

    def convertData(self):
        self.code = self.data[0] # packet code
        self.x = self.data[1:9]  # Estimated x position relative to start (double - 8 bytes)
        self.y = self.data[9:17] # Estimated y position relative to start (double - 8 bytes)
        self.velocity = self.data[17:25] # current velocity (double - 8 bytes)
        self.heading = self.data[25:33]  # heading angle relative to start (double - 8 bytes)
        self.ts_ms = self.data[33:41]  # time stamp in ms since start (uint64_t - 8 bytes)
        self.State = self.data[41:42]  # byte enumeration of node executing state (char - 1 byte)
        self.x_exp = self.data[42:50]  # double
        self.y_exp = self.data[50:58]  # double
        self.velocity_exp = self.data[58:66]  # double
        self.heading_exp = self.data[66:74]  # double
    
    def convertToDict(self):
        dict = vars(self);
        del dict["data"];
        del dict["code"];
        return dict;


class diagnostic_state(Packet):
    def __init__(self, data, code, ts_ms, y_right, d_right, y_left, d_left):
        self.data = data
        self.code = code
        self.ts_ms = ts_ms
        self.y_right = y_right
        self.d_right = d_right
        self.y_left = y_left
        self.d_left = d_left
        self.convertData()

    def convertData(self):
        self.code = self.data[0]  # packet code
        self.ts_ms = self.data[1:9]  # time stamp in ms since start (uint64_t - 8 bytes)
        self.y_right = self.data[9:17]  # double
        self.d_right = self.data[17:25]  # double
        self.y_left = self.data[25:33]  # double
        self.d_left = self.data[33:41]  # double
    
    def convertToDict(self):
        dict = vars(self);
        del dict["data"];
        del dict["code"];
        return dict;


class path_packet(Packet):
    def __init__(self, data, code, x, y):
        self.data = data
        self.code = code
        self.x = x
        self.y = y
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
