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

UAV_LOCAL_IP = "192.168.10.2";
UAV_LOCAL_PORT = 8890;

LOCAL_IP = "192.168.0.104";
UGV_BASE_LOCALS_PORT = 63734;

WEBAPP_LOCALS_PORT = 63733;

NUMBER_OF_UGVS = 1;

async def main():
    mainQueue = asyncio.Queue();

    webapp = Webapp('127.0.0.1', WEBAPP_LOCALS_PORT, mainQueue);
    asyncio.create_task(webapp.start_network());
    
    uav = UAV(UAV_LOCAL_IP, UAV_LOCAL_PORT);
    asyncio.create_task(uav.connect());

    ugvs = [];

    ugvInCritRad = None;
    ugvStopQueue = [];

    # for i in range(NUMBER_OF_UGVS):
    #     ugvs.append(UGV(LOCAL_IP, UGV_BASE_LOCALS_PORT + i, mainQueue));
    #     asyncio.create_task(ugvs[i].start_network());




    pathPlan = None;

    while(1):
        message = await mainQueue.get();
        match(message["source"]):
            case 'webapp':
                match(message["data"]["type"]):
                    case 'scout':
                        print("Scouting");
                        # await uav.send('takeoff');
                        # await uav.send('up 70');
                        # print(f'height: {uav.state_listener.state.h}')
                        img = uav.capture_photo();
                        # height = uav.state_listener.state.h
                        # print(height);
                        # await uav.send('land');
                        height = 150;
                        shape = run_cv(img, height);
                        # img = cv2.imread("./OpenCV/Images/round.jpg");
                        # shape = run_cv(img, 100);
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
                    case 'ugvLoad':
                        await ugvs[message["data"]["data"]].sendNewPath(pathPlan.paths);
            case 'ugv':
                match(message["data"]["type"]):
                    case 'connected':
                        message = {
                            'type': 'ugvAdded',
                            'data': {
                                'id': message["data"]["id"],
                                'name': f'UGV {message["data"]["id"]}',
                                'state': State(0).name,
                            }
                        }; 
                        print(message);
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
                            ugvInCritRad = message["data"]["id"];
                        else:
                            ugvStopQueue.append(message["data"]["id"]);
                            for ugv in ugvs:
                                if(ugv.id == message["data"]["id"]):
                                    ugv.stop();
                                    break;
                    case 'leaveCritRad':
                        if(len(ugvStopQueue) == 0):
                            ugvInCritRad = None;
                        else:
                            ugvId = ugvStopQueue.pop(0);
                            ugvInCritRad = ugvId;
                            for ugv in ugvs:
                                if(ugv.id == ugvId):
                                    ugv.go();
                                    break;





cv2.destroyAllWindows();
asyncio.run(main());

