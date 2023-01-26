class Packet:  # packet objects to store path data and node status data
    def __init__(self, data):
        self.data__ = data

    # byte sizes for different data types:
    # char - 1
    # short - 2
    # int - 4
    # long - 8
    # long long - 8
    # double - 8 bytes
    # uint64_t - 8 bytes
    # we will make our packet size 42 bytes, this accommodates note State (42 bytes) and pathpoint (41 bytes)

    def parseData(self):
        index = 0
        # get list of all variables for an object
        variables = [variable for variable in vars(self)
                     # to exclude a variable from this list, use '__' at the beginning or end of the name
                     if not variable.startswith('__')
                     and not variable.endswith('__')]
        for attr in variables:  # set the value for each variable from the passed in data based on its known size
            length = len(getattr(self, attr))
            setattr(self, attr, self.data__[index: index + length])
            # print('index', index)
            index = index + length
            # print(getattr(packet, attr), length)


class node_state(Packet):  # packet to hold data for the node state
    def __init__(self, data):
        self.data__ = data
        self.packet_size__ = 41
        # set all node state values to 0 by deafult
        self.x = b'00000000'
        self.y = b'00000000'
        self.velocity = b'00000000'
        self.heading = b'00000000'
        self.ts_ms = b'00000000'
        self.state = b'0'
        self.parseData()  # automatically parse data when a new object is created


class path_packet(Packet):  # packet to hold data for path planning

    def __init__(self, *args):
        if len(args) == 1:  # V1 of constructor if we only pass in data array
            self.packet_size__ = 40
            self.data__ = args[0]
            # set all data values to 0 for parseData() to function
            self.x = b'00000000'
            self.y = b'00000000'
            self.velocity = b'00000000'
            self.heading = b'00000000'
            self.ts_ms = b'00000000'
            self.parseData()

        if len(args) > 1:  # V2 of constructor for if we want to manually pass in the variable values alongside the data array
            # order of packet data coming in: data, x, y, velocity, heading, ts_ms
            self.data__ = args[0]
            self.packet_size__ = 40
            self.x = args[1]
            self.y = args[2]
            self.velocity = args[3]
            self.heading = args[4]
            self.ts_ms = args[5]
