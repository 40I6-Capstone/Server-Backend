from Webapp import Webapp;
import asyncio;

LOCAL_IP = "192.168.0.104";
WEBAPP_LOCALS_PORT = 63733;

async def main():

    webapp = Webapp('127.0.0.1', WEBAPP_LOCALS_PORT);
    asyncio.create_task(webapp.start_network());

    while(1):
        await asyncio.sleep(10);

asyncio.run(main());