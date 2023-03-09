from UAV import UAV;
from UGV import UGV;
import asyncio;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

UGV_LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63733;

NUMBER_OF_UGVS = 3;

async def main():

    ugv = [];

    for i in range(NUMBER_OF_UGVS):
        port = UGV_BASE_LOCALS_PORT+i;
        ugv[i] = UGV(UGV_LOCAL_IP, port);
        asyncio.create_task(ugv[i].start_network());

    while(ugv[0].websocket == None):
        print(".");
        await asyncio.sleep(1);
        
    add_msg = asyncio.create_task(ugv.putMessageInQueue("hello world2"));
    await add_msg;
    

    ugv2 = UGV(UGV_LOCAL_IP, UGV_BASE_LOCALS_PORT+1);
    network = asyncio.create_task(ugv2.start_network());
    while(ugv2.websocket == None):
        print(".");
        await asyncio.sleep(1);
        
    add_msg = asyncio.create_task(ugv2.putMessageInQueue("hello world2"));
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

