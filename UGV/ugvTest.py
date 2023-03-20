from UGV import UGV;
import asyncio;

LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63734;

NUMBER_OF_UGVS = 1;

async def main():

    ugv = [None] * NUMBER_OF_UGVS;

    for i in range(NUMBER_OF_UGVS):
        port = UGV_BASE_LOCALS_PORT+i;
        ugv[i] = UGV(LOCAL_IP, port);
        asyncio.create_task(ugv[i].start_network());

    while(1):
        a = input("what to send");
        add_msg = asyncio.create_task(ugv[0].putMessageInQueue(a));
        await add_msg;

asyncio.run(main());
