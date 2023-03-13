import Packet
class Node_state:
    def __init__(self, heading, velocity, X, Y, ts_ms, State, y_right, d_right, y_left, d_left, x_exp, y_exp, velocity_exp, heading_exp):
        self.heading = heading
        self.velocity = velocity
        self.X = X
        self.Y = Y
        self.ts_ms = ts_ms
        self.State = State
        self.y_right = y_right
        self.d_right = d_right
        self.y_left = y_left
        self.d_left = d_left
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
