import socket;
import threading;

host_ports = [];

class UGV:
    def __init__(self, local_ip, local_port, ugv_ip, ugv_port):
        """
        Binds to the local IP/port to the UGV.
        :param host_ip (str): Local IP address to bind.
        :param host_base_port (int): Local port to bind.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

        local_address = (local_ip, local_port);        

        self.socket.bind(local_address);
        self.socket.listen(1);
        self.client, self.client_address = self.socket.accept();
        print("UGV with address %s is connected to the server on %s"%(self.client_address, local_address));

        self.id = len(host_ports);
        host_ports.append((self.id, local_port));

        self.listening_thread = threading.Thread(target=self._networking_thread);
        self.listening_thread.daemon = True;
        self.listening_thread.start();

        self.send_message_queue = [];

    def _networking_thread(self):
        
        while True:
            try:
                self.response = self.client.recv(3000);
                if(self.response):
                    print(self.response.decode())
                if(len(self.send_message_queue)>0):
                    self.client.send(self.send_message_queue.pop().encode())
            except socket.error as err:
                print ("Caught exception UGV receive socket.error : %s" % err);


