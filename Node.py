
# Node class to create 'node' objects for the server. This allows us to reference the nodes by their conn / address as well as store their current state
class Node:
    def __init__(self, conn, address,ID,x,y, velocity, heading, ts_ms, state):
        self.conn = conn # new socket object usable to send and receive data on the connection
        self.address = address # the address bound to the socket on the other end of the connection
        self.ID = ID
        self.status_size = 1
        # Below values will store the current state of the node
        self.x = x
        self.y = y
        self.velocity = velocity
        self.heading = heading
        self.ts_ms = ts_ms
        self.state = state

    def updateState(self, Packet): # method to update the current state to match that of an incoming state packet
        self.heading = Packet.heading
        self.velocity = Packet.velocity
        self.x = Packet.x
        self.y = Packet.y
        self.ts_ms = Packet.ts_ms
        self.state = Packet.state
