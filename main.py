from UAV import UAV;
from UGV import UGV;
from Webapp import Webapp;
import asyncio;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63734;

WEBAPP_LOCALS_PORT = 63733;

NUMBER_OF_UGVS = 1;

async def main():

    webapp = Webapp('127.0.0.1', WEBAPP_LOCALS_PORT);
    asyncio.create_task(webapp.start_network());
    while(webapp.websocket == None):
        print(".");
        await asyncio.sleep(1);
    print("connected to webapp");
    add_msg = asyncio.create_task(webapp.putMessageInQueue("hello world!"));
    await add_msg;

    # ugv = [None] * NUMBER_OF_UGVS;

    # for i in range(NUMBER_OF_UGVS):
    #     port = UGV_BASE_LOCALS_PORT+i;
    #     ugv[i] = UGV(LOCAL_IP, port);
    #     asyncio.create_task(ugv[i].start_network());

    # while(ugv[0].websocket == None):
    #     print(".");
    #     await asyncio.sleep(1);
        
    # add_msg = asyncio.create_task(ugv[0].putMessageInQueue("hello world2"));
    # await add_msg;

    while(1):
        # a = input("what to send");
        await asyncio.sleep(1);
        # add_msg = asyncio.create_task(ugv[0].putMessageInQueue(a));
        # await add_msg;

asyncio.run(main());

