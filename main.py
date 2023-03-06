from UAV import UAV;
from UGV import UGV;
import asyncio;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

UGV_LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63733;

async def main():
    # uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT);
    ugv = UGV(UGV_LOCAL_IP, UGV_BASE_LOCALS_PORT);
    network = asyncio.create_task(ugv.start_network());
    while(ugv.websocket == None):
        await asyncio.sleep(1);
        
    add_msg = asyncio.create_task(ugv.putMessageInQueue("hello world2"));
    await add_msg;
    # print("capture photo");
    # uav.capture_photo();

    # ugv.send_command(command[0]);
    # uav.send_command(command[1]);
    # uav.send_command(command[2]);
    # ugv.send_command(command[3]);

    while(1):
        a = input("what to send");
        add_msg = asyncio.create_task(ugv.putMessageInQueue(a));
        await add_msg;
        # await ugv.send_message_queue.put(a);
        # loop.call_soon_threadsafe(ugv.send_message_queue.put_nowait, a);

        # await ugv.send_message_queue.put(a);
asyncio.run(main());

