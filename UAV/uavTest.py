from UAV import UAV;
import cv2;
import asyncio;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

async def main():
    mainQueue = asyncio.Queue();

    uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT, mainQueue);
    print("creating connection");
    # asyncio.create_task(uav.start_network());
    await uav.connect();
    await asyncio.sleep(1);
    print('Bat', uav.state_listener.state.bat);
    await uav.send('takeoff');
    print(' sent takeoff');
    await asyncio.sleep(5);
    await uav.send('up 70');
    print('sent up70');
    image = uav.capture_photo();
    cv2.imshow('Tello', image)
    cv2.waitKey(1000);
    
    cv2.imwrite('./testImg.jpg', image);

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('./grayTestImg.jpg', gray);
    
    await uav.send('land');   
    # await uav.send('takeoff')
    # await uav.send('land');

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




    # while(1):

    #     uav.capture_photo();
    #     cv2.imshow('Tello', image)
    #     key = cv2.waitKey(1000);
    #     if(key ==27): break;
    # uav.close();  
asyncio.run(main());

