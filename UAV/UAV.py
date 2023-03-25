import socket;
import threading;
import time;
import cv2;
import numpy as np;
import json;

class UavState:
    def __init__(self):
        self.pitch = 0;
        self.roll = 0;
        self.yaw = 0;
        self.vgx = 0;
        self.vgy = 0;
        self.vgz = 0;
        self.templ = 0;
        self.temph = 0;
        self.tof = 0;
        self.h = 0;
        self.bat = 0;
        self.baro = 0;
        self.time = 0;
        self.agx = 0;
        self.agy = 0;
        self.agz = 0;

class UAV:
    def __init__(self, local_ip, local_port, tello_ip="192.168.10.1", tello_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.
        :param local_ip (str): Local WLAN IP address to bind.
        :param local_port (int): Local port to bind.
        :param tello_ip (str): Tello IP.
        :param tello_port (int): Tello port.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        self.uav_address = (tello_ip, tello_port);
        self.tello_ip = tello_ip;
        self.image_port = 11111;

        self.state = UavState();
        
        # set up socket for sending commands to tello drone
        self.socket.bind((local_ip, local_port));
        # start listening for any acks or state updates from the tello drone
        self.listening_thread = threading.Thread(target=self._listening_thread);
        self.listening_thread.daemon = True;
        self.listening_thread.start();

        self.send_command("command");
        self.send_command("streamon");

    
    def _listening_thread(self):
        """
        Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        """
        
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000);
                match (self.response.decode()):
                    case 'ok':
                        print("got command ok");
                    case 'error':
                        print("error sending command");
                    case other:
                        # self.state = json.loads(self.response);
                        stateArr = self.response.decode().replace("\\r\\n","").split(';');
                        for data in stateArr:
                            if(not ":" in data): continue;
                            splitData = data.split(":");
                            setattr(self.state, splitData[0], splitData[1]);
                # if(self.response.decode() == 'ok'): print('ok');
                # print(self.response)
            except socket.error as err:
                print ("Caught exception UGV receive socket.error : %s" % err);
    
    def send_command(self, command):
        self.socket.sendto(command.encode("utf-8"), self.uav_address);
        print("send command: %s to %s"%(command, self.uav_address));
    
    def capture_photo(self):
        cap = cv2.VideoCapture(f'udp://@{self.tello_ip}:{self.image_port}');
        gotFrame = False;
        while(not gotFrame):
            gotFrame, frame = cap.read();
        cap.release();
        cv2.imwrite(f'./pictures/tello_photo{time.strftime("%Y%m%d-%H%M%S")}.jpeg', frame);
        return(frame);

    def close(self):
        self.send_command("streamoff");
        self.socket.close();

        




