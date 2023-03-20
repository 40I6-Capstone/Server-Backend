from UAV.UAV import UAV;
from UGV.UGV import UGV;
from Webapp.Webapp import Webapp;
from OpenCV.OpenCV import run_cv;
from PathPlanning.PathPlanning import PathPlanning;
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





    while(1):
        message = await mainQueue.get();
        match(message["source"]):
            case 'webapp':
                match(message["data"]["type"]):
                    case 'scout':
                        print("Scouting");
                        img = cv2.imread("./OpenCV/Images/round.jpg");
                        shape = run_cv(img);
                        pathPlan = PathPlanning();
                        pathPlan.planPath(shape, 20, 3, 5);
                        paths = [];
                        for path in pathPlan.paths:
                            paths.append(path.points.tolist());
                        message = {
                            "type": "scout",
                            "data": {
                                "paths": paths,
                                "vertices": shape.vertices.tolist(),
                                "midpoints": shape.midpoints.tolist(),
                                "contour": shape.contour.tolist(),
                            }
                        };
                        await webapp.putMessageInQueue(json.dumps(message));

asyncio.run(main());

