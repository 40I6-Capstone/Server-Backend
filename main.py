from UAV.UAV import UAV;
from UGV.UGV import UGV;
from Webapp.Webapp import Webapp;
import asyncio;
import json;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63734;

WEBAPP_LOCALS_PORT = 63733;

NUMBER_OF_UGVS = 1;

async def main():

    webapp = Webapp('127.0.0.1', WEBAPP_LOCALS_PORT);
    asyncio.create_task(webapp.start_network());

    while(1):
        a = input("what to send");
        await asyncio.sleep(10);

asyncio.run(main());

