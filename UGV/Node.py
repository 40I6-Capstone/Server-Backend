import UGV.Packet as Packet
class Node_state:
    def __init__(self, x, y, velocity, heading, ts_ms, State, x_exp, y_exp, velocity_exp, heading_exp):
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



    # def updateState(self, Packet):
    #     self.heading = Packet.heading
    #     self.velocity = Packet.velocity
    #     self.X = Packet.X
    #     self.Y = Packet.Y
    #     self.ts_ms = Packet.ts_ms
    #     self.State = Packet.State
