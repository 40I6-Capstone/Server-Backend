import math;
import numpy as np;
import scipy.interpolate as si
import scipy.spatial as ss
from OpenCV.OpenCV import Shape

class Path:
    def __init__(self, points):
        self.points = points;
        self.length = np.sum(np.sqrt(np.diff(points[:,0])**2 + np.diff(points[:,1])**2))       

class PathPlanning:
    def __init__(self):
        self.paths = [];
        
    def planPath(self, shape:Shape, crit_rad, ugv_rad, spoke_len):
       # calculate the angle from the origin to the centre of the shape
        base_angle = math.atan(shape.centre[1]/shape.centre[0]);
        # calculate how many paths we need to plan
        num_of_paths = len(shape.midpoints);

        self.crit_rad = crit_rad;

        # calculate the angle the ugv's will leave from the origin for its own lane
        d_angle = 2*math.asin((1.05*(ugv_rad/2))/crit_rad);

        # keep values within a certain angle
        if(d_angle * num_of_paths > math.pi/2):
            d_angle = math.pi / (2*num_of_paths);
            self.crit_rad = 1.05*(ugv_rad/2)/math.sin(d_angle/2);
            print(f'New Crit Radius {self.crit_rad}');

        
        # number of points for 1st part of the path (in the crit circle)
        nop_1 = 3;
        d_rad = self.crit_rad/nop_1;

        # number of points for the 3rd part of the path (the spoke length)
        nop_3 = 3;
        d_len_3 = spoke_len/50;


        for i in range(num_of_paths):
            path1 = [[0,0]];
            path2 = [];
            path3 = [];
            cv = [];

            if(i%2):
                angle_off = i*d_angle;
                shape_i = int(-(i+1)/2);

            else:
                angle_off = -(i + 1)*d_angle;
                shape_i = int(i/2);
            
            ctl_ext = self._get_ext_coef(ugv_rad);

            # calculate the points for inside the critical circle
            for j in range(nop_1):
                cr_x = j*d_rad*math.cos((base_angle+angle_off));
                cr_y = j*d_rad*math.sin((base_angle+angle_off));
                path1.append([cr_x,cr_y]);
            # add the end of path 1 to the control points (start anchor)
            cv.append([cr_x,cr_y]);

            # add the extension to the path 1 to the control points (off path)
            cr_x_ext = (self.crit_rad + ctl_ext[0])*math.cos((base_angle+angle_off));
            cr_y_ext = (self.crit_rad + ctl_ext[0])*math.sin((base_angle+angle_off));
            cv.append([cr_x_ext,cr_y_ext]);
            
            # add the extension to the spoke path to the control points (off path)
            sp_x_ext = shape.midpoints[shape_i,0] + (spoke_len + ctl_ext[1])*shape.norms[shape_i,0];
            sp_y_ext = shape.midpoints[shape_i,1] + (spoke_len + ctl_ext[1])*shape.norms[shape_i,1];
            cv.append([sp_x_ext,sp_y_ext]);

            #calculate the values for the spoke path
            for k in range(nop_3):
              sp_x = shape.midpoints[shape_i,0] + k*d_len_3*shape.norms[shape_i,0];
              sp_y = shape.midpoints[shape_i,1] + k*d_len_3*shape.norms[shape_i,1];
              path3.append([sp_x,sp_y]);
            # add the end of path 3 to the control points (end anchor)
            cv.append([sp_x,sp_y]);

            # reverse the path so it goes towards the shape
            path3.reverse();

            # calculate the path points for the cubic b spline (path 2)
            cv = np.array(cv);
            path2 = self._b_spline(cv);

            # concatenate the 3 path parts to get the complete path and add it to the path list 
            path = Path(np.array(path1+path2+path3))
            self.paths.append(path);  
            if len(self.paths) > 2:
                path_dist = ss.distance.cdist(path2, self.paths[-3].points[nop_1:-1]);
                coll_index =  np.where(path_dist < 2*ugv_rad);
                while(len(coll_index[0]) > 0):
                    # get the point where the collision will occur
                    path2_np = np.array(path2);

                    coll_dist_to_rad = np.sum(np.sqrt(np.diff(path2_np[0:coll_index[0][0],0])**2 + np.diff(path2_np[0:coll_index[0][0],1])**2))
                    coll_dist_to_spoke = 0.7*(np.sum(np.sqrt(np.diff(path2_np[coll_index[0][0]:-1,0])**2 + np.diff(path2_np[coll_index[0][0]:-1,1])**2)))
                    
                    ctl_ext = self._get_ext_coef(ugv_rad, ctl_ext, "rad" if (coll_dist_to_rad<coll_dist_to_spoke) else "spoke");
                    cr_x_ext = (self.crit_rad + ctl_ext[0])*math.cos((base_angle+angle_off));
                    cr_y_ext = (self.crit_rad + ctl_ext[0])*math.sin((base_angle+angle_off));
                    cv[1] = np.array([cr_x_ext,cr_y_ext]);

                    sp_x_ext = shape.midpoints[shape_i,0] + (spoke_len + ctl_ext[1])*shape.norms[shape_i,0];
                    sp_y_ext = shape.midpoints[shape_i,1] + (spoke_len + ctl_ext[1])*shape.norms[shape_i,1];
                    cv[2] = np.array([sp_x_ext,sp_y_ext]);

                    path2 = self._b_spline(cv);
                    path_dist = ss.distance.cdist(path2, self.paths[-3].points[nop_1:-1]);
                    coll_index =  np.where(path_dist < 2*ugv_rad);

                    # concatenate the 3 path parts to get the complete path and add it to the path list 
                    path = Path(np.array(path1+path2+path3))
                    self.paths[-1] = path;
      
    
    # function to get how much the control points should extend by from the anchor points
    def _get_ext_coef(self, ugv_rad, ctl_ext=[], side=None):
            if(len(ctl_ext) == 0):
                ctl_rad_ext =  ugv_rad;
                ctl_spoke_ext = ugv_rad;
            else:
                [ctl_rad_ext, ctl_spoke_ext] = ctl_ext;
                if(side == "rad"):
                    ctl_rad_ext = ctl_ext[0] + ugv_rad;
                elif(side == "spoke"):
                    ctl_spoke_ext = ctl_ext[1] + ugv_rad;
            return np.array([ctl_rad_ext, ctl_spoke_ext]);

    def _b_spline(self, cv):
        n=50;
        cv = np.asarray(cv);
        count = cv.shape[0];
        degree = 2;

        # Prevent degree from exceeding count-1, otherwise splev will crash
        degree = np.clip(degree,1,count-1);

        # Calculate knot vector
        kv = np.array([0]*degree + list(range(count-degree+1)) + [count-degree]*degree,dtype='int');

        # Calculate query range
        u = np.linspace(0,(count-degree),n);

        # Calculate result
        return np.array(si.splev(u, (kv,cv.T,degree))).T.tolist();