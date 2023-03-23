import machine
import time

# Define the pins to use
tx_pin = machine.Pin(0)  # GP0
rx_pin = machine.Pin(1)  # GP1

# Initialize the UART interface
uart = machine.UART(0, baudrate=115200, tx=tx_pin, rx=rx_pin)

class node_state():
    def __init__(self, data):
        self.data = data
        self.code = None
        self.x = None
        self.y = None
        self.velocity = None
        self.heading = None
        self.ts_ms = None
        self.State = None
        self.x_exp = None
        self.y_exp = None
        self.velocity_exp = None
        self.heading_exp = None
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
    response = response.decode('utf-8')
    print("response 2:   " + response)
    
    if(response[0] == '1'): # send node state
        #print('got in 1!')
        data = code + state_history.pop(0).data + combined
        state = node_state(data)
        print(state.data)
        uart.write(state.data)
    elif(response[0] == '2'): # Receive path packet
        #print('got in 2!')
        path = path_packet(response)
        state_history.append(path)
