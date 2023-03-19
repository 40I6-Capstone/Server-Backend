from UAV import UAV;
import cv2;
import asyncio;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

async def main():

    uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT);
    await asyncio.sleep(1);
    uav.send_command("takeoff");
    await asyncio.sleep(1);
    uav.send_command("up 200");
    image = uav.capture_photo();
    await asyncio.sleep(1);
    uav.send_command("down 100");
    cv2.imshow('Tello', image)
    await asyncio.sleep(3);
    uav.send_command("land");
    await asyncio.sleep(3);



    # while(1):
    #     uav.capture_photo();
    #     cv2.imshow('Tello', image)
    #     key = cv2.waitKey(1000);
    #     if(key ==27): break;
    uav.close();  
asyncio.run(main());

