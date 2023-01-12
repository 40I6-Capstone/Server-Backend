from UAV import UAV;
from UGV import UGV;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

UGV_LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63733;

UGV_IP = "192.168.0.115";
UGV_PORT = 5000;

command = ["hello", "takeoff", "land", "bye"];

uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT);
ugv = UGV(UGV_LOCAL_IP, UGV_BASE_LOCALS_PORT, UGV_IP, UGV_PORT);

uav.send_command("command");

ugv.send_command(command[0]);
uav.send_command(command[1]);
uav.send_command(command[2]);
ugv.send_command(command[3]);


input("press key to end")


