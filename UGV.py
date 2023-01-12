import socket;
import threading;

host_ports = [];

class UGV:
    def __init__(self, local_ip, base_local_port, ugv_ip, ugv_port):
        """
        Binds to the local IP/port to the UGV.
        :param host_ip (str): Local IP address to bind.
        :param host_base_port (int): Local port to bind.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        # self.ugv_address = (ugv_ip, ugv_port);

        self.id = len(host_ports);
        local_address = (local_ip, base_local_port);
        print(local_address);
        
        # host_ports.append((self.id, local_port));

        self.socket.bind(local_address);
        print("socket binded");
        self.socket.listen();
        print("socket listening for connections");
        self.client, self.client_connection = self.socket.accept();
        print("client connected");

        # self.socket.connect((ugv_ip, ugv_port));

        self.listening_thread = threading.Thread(target=self._listening_thread);
        self.listening_thread.daemon = True;
        self.listening_thread.start();

    def _listening_thread(self):
        """
        Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        """
        
        while True:
            try:
                self.response = self.client.recv(3000);
                if(self.response):
                    print(self.response.decode())
            except socket.error as err:
                print ("Caught exception UGV receive socket.error : %s" % err);

    
    def send_command(self, command):
        self.client.send(command.encode());
        print("sending command: %s"%(command));

