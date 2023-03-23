import machine
import time

# Define the pins to use
tx_pin = machine.Pin(0)  # GP0
rx_pin = machine.Pin(1)  # GP1

# Initialize the UART interface
uart = machine.UART(0, baudrate=115200, tx=tx_pin, rx=rx_pin)

class node_state():
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

class path_packet():
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

code = '1'
velocity = '00000000'
heading = '00000000'
ts_ms = '00000000'
State = '00000000'
x_exp = '00000000'
y_exp = '00000000'
velocity_exp = '00000000'
heading_exp = '00000000'
combined = velocity + heading + ts_ms + State + x_exp + y_exp + velocity_exp + heading_exp

state_history = []

while(1):
    # Wait for data to be sent over serial
    while not uart.any():
        pass

    # Read the response from the ESP8266 module
    response = uart.read()
    print(response)
    
    if(response[0] == '1'): # send node state
        data = code + state_history.pop(0).data + combined
        state = node_state(data)
        uart.write(state)
    elif(response[0] == '2'): # Receive path packet
        path = path_packet(response)
        state_history.append(path)
