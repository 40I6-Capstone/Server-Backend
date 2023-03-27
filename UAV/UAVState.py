import asyncio;

STATE_FIELDS = ['raw', 'roll', 'pitch', 'yaw', 'height', 'barometer', 'battery', 'time_of_flight', 'motor_time', 'temperature', 'acceleration', 'velocity', 'mission_pad', 'mission_pad_position']
class UavState:
    def __init__(self, pitch = 0, roll = 0, yaw = 0, vgx = 0.0, vgy = 0.0, vgz = 0.0, templ = 0, temph = 0, tof = 0, h = 0, bat = 0, baro = 0.0, time = 0, agx = 0.0, agy = 0.0, agz = 0.0):
        self.pitch = pitch;
        self.roll = roll;
        self.yaw = yaw;
        self.vgx = vgx;
        self.vgy = vgy;
        self.vgz = vgz;
        self.templ = templ;
        self.temph = temph;
        self.tof = tof;
        self.h = h;
        self.bat = bat;
        self.baro = baro;
        self.time = time;
        self.agx = agx;
        self.agy = agy;
        self.agz = agz;

class UAVStateListener:

    _transport = None
    state = None;

    class Protocol:
        def connection_made(self, transport):
            pass

        def datagram_received(self, data, addr):
            message = data.decode('ascii')
            # print('[state] RECEIVED', message)
            state = parse_state_message(message)
            self.on_state_received(state)

        def error_received(self, error):
            print('[state] PROTOCOL ERROR', error)

        def connection_lost(self, error):
            # print('[state] CONNECTION LOST', error)
            pass

    def __init__(self, local_ip, local_port, main_queue: asyncio.Queue):
        self._local_ip = local_ip
        self._local_port = local_port
        self.main_queue = main_queue
        self.count = 0;

    async def connect(self, loop):
        transport, protocol = await loop.create_datagram_endpoint(
            UAVStateListener.Protocol, 
            local_addr=(self._local_ip, self._local_port)
        )
        self._transport = transport
        protocol.on_state_received = self.updateState; 

    async def disconnect(self):
        if self._transport:
            self._transport.close()
            self._transport = None
            self.state = UavState();

    def updateState(self, state: UavState):
        if(state == None): return;
        self.count += 1;
        if(self.count == 1):
            self.state = state;
            message = {
                'source': 'UAV',
                'data': {
                    'type': 'sendBat',
                    'data': self.state.bat,
                }
            };
            asyncio.get_running_loop().create_task(self.main_queue.put(message));
        elif(self.count == 100): 
            self.count = 0
        


def parse_state_message(raw):
    pairs = [p.split(':') for p in raw.rstrip(';\r\n').split(';')]
    value_map = { p[0]:p[1] for p in pairs }

    def get_int_value(key):
        try:
            return int(value_map[key])
        except KeyError:
            return None

    def get_float_value(key):
        try:
            return float(value_map[key])
        except KeyError:
            return None


    pitch = get_int_value('pitch')
    roll = get_int_value('roll')
    yaw = get_int_value('yaw')
    vgx = get_float_value('vgx')
    vgy = get_float_value('vgy')
    vgz = get_float_value('vgz')
    templ = get_int_value('templ')
    temph = get_float_value('temph')
    tof = get_int_value('tof')
    h = get_int_value('h')
    bat = get_int_value('bat')
    baro = get_float_value('baro')
    time = get_int_value('time')
    agx = get_float_value('agx')
    agy = get_float_value('agy')
    agz = get_float_value('agz')

    return UavState(pitch, roll, yaw, vgx, vgy, vgz, templ, temph, tof, h, bat, baro, time, agx, agy, agz);
