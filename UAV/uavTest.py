from UAV import UAV;
import cv2;
import asyncio;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

async def main():

    uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT);
    print("creating connection");
    # asyncio.create_task(uav.start_network());
    await uav.connect();
    await uav.send('takeoff')
    image = uav.capture_photo();
    await uav.send('land');
    cv2.imshow('Tello', image)
    cv2.waitKey(1000);

    # for i in range(10):
    #     print(uav.state_listener.state.h);
    #     await asyncio.sleep(0.1);
    #     await uav.send(f'up {(i+2)*10}')
    # await uav.send('land');
    # while (not uav.connected);
    #     await asyncio.sleep(1);

    # await asyncio.sleep(1);
    # uav.send_command("takeoff");
    # await asyncio.sleep(1);
    # uav.send_command("up 200");
    # image = uav.capture_photo();
    # await asyncio.sleep(1);
    # uav.send_command("down 100");
    # cv2.imshow('Tello', image)
    # await asyncio.sleep(3);
    # uav.send_command("land");
    # await asyncio.sleep(3);




    while(1):

        uav.capture_photo();
        cv2.imshow('Tello', image)
        key = cv2.waitKey(1000);
        if(key ==27): break;
    # uav.close();  
asyncio.run(main());

