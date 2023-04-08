from UAV.UAV import UAV;
from UGV.UGV import UGV;
from UGV.Packet import State;
from Webapp.Webapp import Webapp;
from OpenCV.OpenCV import run_cv;
import OpenCV.Aruco as Aruco;
from PathPlanning.PathPlanning import PathPlanning;
from PathPlanning.PathScheduler import PathScheduler;
import asyncio;
import cv2;
import json;
import base64;
import time;

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63734;

WEBAPP_LOCALS_PORT = 63733;

NUMBER_OF_UGVS = 4;


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

    ugvConnections = [];
    ugvs = [];

    ugvInCritRad = None;
    ugvStopQueue = [];

    numberOfActiveUGVs = 0;
    pathScheduler = None;
    pathPlan = None;

    timeStart = time.time_ns()*1000000;

    pixel_ratio = 0;
    image_offset = 0;

    for i in range(NUMBER_OF_UGVS):
        ugvConnections.append(UGV(LOCAL_IP, UGV_BASE_LOCALS_PORT, i, timeStart, mainQueue));
        ugvTask = asyncio.create_task(ugvConnections[i].start_network());
        backgroundtasks.add(ugvTask);
        ugvTask.add_done_callback(backgroundtasks.discard);




    pathPlan = None;

    while(1):
        message = await mainQueue.get();
        match(message["source"]):
            case 'webapp':
                match(message["data"]["type"]):
                    case 'scout':
                        numberOfActiveUGVs = message["data"]["data"];
                        print("Scouting");
                        # await uav.send('takeoff');
                        # await uav.send('forward 70');
                        # await uav.send('up 70');
                        # img = uav.capture_photo();
                        img = cv2.imread("./OpenCV/Images/testImg.jpg");
                        [pixel_ratio, image_offset] = Aruco.pixel_to_cm_ratio_from_frame(img);
                        shape = run_cv(cv2.flip(img,0), pixel_ratio, image_offset);
                        pathPlan = PathPlanning();
                        pathPlan.planPath(shape, 9, 5, numberOfActiveUGVs);
                        pathScheduler = PathScheduler(numberOfActiveUGVs, pathPlan.paths);
                        for ugv in ugvs:
                            if(ugv.id >= numberOfActiveUGVs): continue;
                            ugv.setCritRad(pathPlan.crit_rad);
                            ugv.setPaths(pathScheduler.assignedPathIndexes[ugv.id])
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
                                "dim": [img.shape[1]/pixel_ratio, img.shape[0]/pixel_ratio],
                                "off": (image_offset).tolist(),
                            }
                        };
                        await webapp.putMessageInQueue(json.dumps(message));
                        
                    case 'giveUgvPath':
                        print(f'give ugv {message["data"]["data"]} a path');
                        for ugv in ugvs:
                            if(ugv.id == message["data"]["data"]):
                                await ugv.sendNewPath(pathPlan.paths);
                                break;
                    case 'takeUgv':
                        if(len(ugvStopQueue) == 0):
                            ugvInCritRad = None;
                        else:
                            ugvId = ugvStopQueue.pop(0);
                            print(f'ugv {ugvId} entering crit rad')
                            ugvInCritRad = ugvId;
                            await ugvs[ugvId].go();
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
                    case 'stopSingle':
                        for ugv in ugvs:
                            if(ugv.id == message["data"]["data"]):
                                ugv.stopDiagPath();
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
                        if(not len(ugvs) == message["data"]["id"]): print("MISMATCH in UGV INDEX");
                        for ugv in ugvConnections:
                            if (ugv.id == message["data"]["id"]):
                                ugvs.append(ugv);
                                if(not pathScheduler == None):
                                    ugvs[ugv.id].setCritRad(pathPlan.crit_rad);
                                    ugvs[ugv.id].setPaths(pathScheduler.assignedPathIndexes[ugv.id])
                                break;
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
                            await ugvs[message["data"]["id"]].stop();
                    case 'leaveCritRad':
                        print(f'ugv {ugvInCritRad} leaving crit rad')
                        if(len(ugvStopQueue) == 0):
                            ugvInCritRad = None;
                        else:
                            ugvId = ugvStopQueue.pop(0);
                            print(f'ugv {ugvId} entering crit rad')
                            ugvInCritRad = ugvId;
                            await ugvs[ugvId].go();
                    case 'placeBoom':
                        ugv = ugvs[message["data"]["id"]];
                        img = uav.capture_photo()
                        posData = Aruco.getNodePosition(img, ugv.arucoId, pixel_ratio, image_offset);
                        asyncio.create_task(ugvs.handleBoomPlacement(posData));
                        message = {
                            "type": "ugvPlaceBoom",
                            "data": {
                                "pathIndex": message["data"]["pathIndex"],
                                "ugvId": message["data"]["ugvId"]
                            }
                        }
                        await webapp.putMessageInQueue(json.dumps(message));
                    case 'finishPath':
                        ugv = ugvs[message["data"]["id"]];
                        img = uav.capture_photo()
                        posData = Aruco.getNodePosition(img, ugv.arucoId, pixel_ratio, image_offset);
                        await ugv.sendAbsolutePos(posData);
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

