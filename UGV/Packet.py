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
    def __init__(self, data, x, y, velocity, heading, ts_ms, State, x_exp, y_exp, velocity_exp, heading_exp):
        self.data = data
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

    def convertData(self):
        self.x = self.data[0:8]  # Estimated x position relative to start (double - 8 bytes)
        self.y = self.data[8:16] # Estimated y position relative to start (double - 8 bytes)
        self.velocity = self.data[16:24] # current velocity (double - 8 bytes)
        self.heading = self.data[24:32]  # heading angle relative to start (double - 8 bytes)
        self.ts_ms = self.data[32:40]  # time stamp in ms since start (uint64_t - 8 bytes)
        self.State = self.data[40:41]  # byte enumeration of node executing state (char - 1 byte)
        self.x_exp = self.data[41:49]  # double
        self.y_exp = self.data[49:57]  # double
        self.velocity_exp = self.data[57:65]  # double
        self.heading_exp = self.data[65:73]  # double


class diagnostic_state(Packet):
    def __init__(self, data, ts_ms, y_right, d_right, y_left, d_left):
        self.data = data
        self.ts_ms = ts_ms
        self.y_right = y_right
        self.d_right = d_right
        self.y_left = y_left
        self.d_left = d_left

    def convertData(self):
        self.ts_ms = self.data[0:8]  # time stamp in ms since start (uint64_t - 8 bytes)
        self.y_right = self.data[8:16]  # double
        self.d_right = self.data[16:24]  # double
        self.y_left = self.data[24:32]  # double
        self.d_left = self.data[32:40]  # double


class path_packet(Packet):
    def __init__(self, data, x, y, ts_ms, v, heading):
        self.data = data
        self.x = x
        self.y = y
        self.ts_ms = ts_ms
        self.v = v
        self.heading = heading

    def convertData(self):
        self.x = self.data[0:8]  # x position for path point (double - 8 bytes)
        self.y = self.data[8:16]  # y position for path point (double - 8 bytes)
        self.ts_ms = self.data[16:24]  # time stamp in ms of when this point should be hit (uint64_t - 8 bytes)
        self.v = self.data[24:32]  # velocity at this point (double - 8 bytes)
        self.heading = self.data[32:40]  # heading at this point (double - 8 bytes)

#
# class NodeManager:
#     def __init__(self, id, ws):
#         self.id = id
#         self.ws = ws


# one fsm branches between packet codes, sub FSM handles conversation back and forth between
# draw the FSM before coding
