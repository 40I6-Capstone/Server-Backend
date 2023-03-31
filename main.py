from UAV.UAV import UAV;
from UGV.UGV import UGV;
from UGV.Packet import State;
from Webapp.Webapp import Webapp;
from OpenCV.OpenCV import run_cv;
from PathPlanning.PathPlanning import PathPlanning;
from PathPlanning.PathScheduler import PathScheduler;
import asyncio;
import cv2;
import json;
import base64;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63734;

WEBAPP_LOCALS_PORT = 63733;

NUMBER_OF_UGVS = 1;

def encode_img(img, im_type):
    """Encodes an image as a png and encodes to base 64 for display."""
    success, encoded_img = cv2.imencode('.{}'.format(im_type), img)
    if success:
        return base64.b64encode(encoded_img).decode()
    return ''

async def main():
    backgroundtasks = set();

    mainQueue = asyncio.Queue();

    webapp = Webapp('127.0.0.1', WEBAPP_LOCALS_PORT, mainQueue);
    webappTask = asyncio.create_task(webapp.start_network());
    backgroundtasks.add(webappTask);
    webappTask.add_done_callback(backgroundtasks.discard);
    
    uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT, mainQueue);
    uavTask = asyncio.create_task(uav.connect());
    backgroundtasks.add(uavTask);
    uavTask.add_done_callback(backgroundtasks.discard);

    ugvs = [];

    ugvInCritRad = None;
    ugvStopQueue = [];

    for i in range(NUMBER_OF_UGVS):
        ugvs.append(UGV(LOCAL_IP, UGV_BASE_LOCALS_PORT + i, mainQueue));
        ugvTask = asyncio.create_task(ugvs[i].start_network());
        backgroundtasks.add(ugvTask);
        ugvTask.add_done_callback(backgroundtasks.discard);




    pathPlan = None;

    while(1):
        message = await mainQueue.get();
        match(message["source"]):
            case 'webapp':
                match(message["data"]["type"]):
                    case 'scout':
                        print("Scouting");
                        # await uav.send('takeoff');
                        # await uav.send('forward 70');
                        # await uav.send('up 70');
                        # img = uav.capture_photo();
                        img = cv2.imread("./OpenCV/Images/testImg.jpg");
                        [shape, imgWidthCm, imgHeightCm] = run_cv(cv2.flip(img,0));
                        pathPlan = PathPlanning();
                        pathPlan.planPath(shape, 20, 3, 5);
                        pathScheduler = PathScheduler(NUMBER_OF_UGVS, pathPlan.paths);
                        for ugvIndex,ugv in enumerate(ugvs):
                            ugv.setCritRad(pathPlan.crit_rad);
                            ugv.setPaths(pathScheduler.assignedPathIndexes[ugvIndex])
                        paths = [];
                        for path in pathPlan.paths:
                            paths.append(path.points.tolist());
                        message = {
                            "type": "scout",
                            "data": {
                                "paths": paths,
                                "vertices": shape.vertices.tolist(),
                                "midpoints": shape.midpoints.tolist(),
                                "contour": [],#shape.contour.tolist(),
                            }
                        };
                        await webapp.putMessageInQueue(json.dumps(message));

                        encoded_img = encode_img(img, 'jpg')
                        b64_src = 'data:image/jpeg;base64,'
                        img_src = b64_src + encoded_img
                        message = {
                            "type": "imageUpdate",
                            "data": {
                                "src": img_src,
                                "dim": [imgWidthCm, imgHeightCm],
                                "off": [0,0],
                            }
                        };
                        await webapp.putMessageInQueue(json.dumps(message));
                        # await uav.send('land');
                        
                    case 'giveUgvPath':
                        print(f'give ugv {message["data"]["data"]} a path');
                        for ugv in ugvs:
                            if(ugv.id == message["data"]["data"]):
                                await ugv.sendNewPath(pathPlan.paths);
                                break;
                    case 'reconnectUav':
                        print ('reconnectUav');
                        uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT, mainQueue);
                        uavTask = asyncio.create_task(uav.connect());
                        uavTask.add_done_callback(backgroundtasks.discard);
                    case 'startSingle':
                        for ugv in ugvs:
                            if(ugv.id == message["data"]["data"]["id"]):
                                await ugv.sendDefinedPath(message["data"]["data"]["path"]);
                                break;

                        
            case 'ugv':
                match(message["data"]["type"]):
                    case 'connected':
                        message = {
                            'type': 'ugvAdded',
                            'data': {
                                'id': message["data"]["id"],
                                'name': f'UGV {message["data"]["id"]}',
                                'port': message["data"]["port"],
                                'state': State(0).name,
                            }
                        }; 
                        await webapp.putMessageInQueue(json.dumps(message));
                    case 'state':
                        message = {
                            'type': 'ugvState',
                            'data': {
                                'id': message["data"]["id"],
                                'data': message["data"]["data"],
                            }
                        };
                        await webapp.putMessageInQueue(json.dumps(message));
                    case 'diagState':
                        message = {
                            'type': 'ugvDiagState',
                            'data': {
                                'id': message["data"]["id"],
                                'data': message["data"]["data"],
                            }
                        }
                        await webapp.putMessageInQueue(json.dumps(message));
                    case 'enterCritRad':
                        if(ugvInCritRad == None):
                            print(f'ugv {message["data"]["id"]} entering crit rad')
                            ugvInCritRad = message["data"]["id"];
                        else:
                            print(f'stop ugv {message["data"]["id"]}')
                            ugvStopQueue.append(message["data"]["id"]);
                            for ugv in ugvs:
                                if(ugv.id == message["data"]["id"]):
                                    await ugv.stop();
                                    break;
                    case 'leaveCritRad':
                        print(f'ugv {ugvInCritRad} leaving crit rad')
                        if(len(ugvStopQueue) == 0):
                            ugvInCritRad = None;
                        else:
                            ugvId = ugvStopQueue.pop(0);
                            print(f'ugv {ugvId} entering crit rad')
                            ugvInCritRad = ugvId;
                            for ugv in ugvs:
                                if(ugv.id == ugvId):
                                    await ugv.go();
                                    break;
                    case 'placeBoom':
                        message = {
                            "type": "ugvPlaceBoom",
                            "data": {
                                "pathIndex": message["data"]["pathIndex"],
                                "ugvId": message["data"]["ugvId"]
                            }
                        }
                        await webapp.putMessageInQueue(json.dumps(message));
                    case 'finishPath':
                        print('send finish path');
                        message = {
                            "type": "ugvDonePath",
                            "data": {
                                "pathIndex": message["data"]["pathIndex"],
                                "ugvId": message["data"]["ugvId"]
                            }
                        }
                        await webapp.putMessageInQueue(json.dumps(message));
            case 'UAV':
                match(message["data"]["type"]):
                    case 'connected':
                        message = {
                            'type': 'uavConnected',
                        }
                        await webapp.putMessageInQueue(json.dumps(message));
                    case 'disconnected':
                        message = {
                            'type': 'uavDisconnected',
                        }
                        await webapp.putMessageInQueue(json.dumps(message));
                    case 'sendBat':
                        message = {
                            'type': 'updateBatState',
                            'data': message["data"]["data"],
                        }
                        await webapp.putMessageInQueue(json.dumps(message));
        mainQueue.task_done();






cv2.destroyAllWindows();
asyncio.run(main());

