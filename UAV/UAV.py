import socket;
import threading;
import time;
import cv2;
import numpy as np;

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

        




