'''
Created on 20 nov. 2014

@author: Bernard
'''
import cv2
import numpy
import math
import copy
import sys

SMOOTHING_RADIUS = 30
HORIZONTAL_BORDER_CROP = 20

class TransformParam:
    def __init__(self,dx,dy,da):
        self.dx = dx
        self.dy = dy
        self.da = da

if __name__ == '__main__':
    cap = cv2.VideoCapture(r'D:\Users\Bernard\Documents\My Projects\GoPro\GOPR5789.MP4')
#    cap = cv2.VideoCapture(r'D:\Users\Bernard\Videos\chuck s03\chuck.301.vostf.avi')
    assert(cap.isOpened())
        
    ret,prev = cap.read()
    prev_grey = cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY)
    
    # Step 1 - Get previous to current frame transformation (dx, dy, da) for all frames
    prev_to_cur_transform = []
    k = 1
    max_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    last_transform = numpy.ndarray((1,1,2))
    
    while(True):
        ret,cur = cap.read()
        if ((ret == False) and (cur == None)):
            break
        cur_grey = cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY)
        
        # Vector from prev to cur  
        prev_corner = cv2.goodFeaturesToTrack(prev_grey,200,0.01,30)
        cur_corner,status,err = cv2.calcOpticalFlowPyrLK(prev_grey, cur_grey, prev_corner)
        
        prev_corner2 = numpy.ndarray((1,1,2));
        cur_corner2 = numpy.ndarray((1,1,2));
        first = False
        # Weed out bad matches
        for i,st in enumerate(status):
            if (st == 1):
                if (first == False):
                    prev_corner2[0] = prev_corner[0]
                    cur_corner2[0] = cur_corner[0]
                    first = True
                else:
                    prev_corner2 = numpy.vstack((prev_corner2,prev_corner[i].reshape((1,1,2)))) 
                    cur_corner2 = numpy.vstack((cur_corner2,cur_corner[i].reshape((1,1,2))))
        
        # Translation + rotation only
        cur_corner2 = cur_corner2.astype(numpy.int)
        prev_corner2 = prev_corner2.astype(numpy.int)
        
        transform = cv2.estimateRigidTransform(prev_corner2, cur_corner2, False)  

        # In rare cases no transform is found, We'll just use the last known good transform.
        if (transform.data == None):
            transform = last_transform.copy()
            
        last_transform = transform.copy()
        
        # decompose transform
        dx = transform[0,2]
        dy = transform[1,2]
        da = math.atan2(transform[1,0], transform[0,0])
        
        prev_to_cur_transform.append(TransformParam(dx,dy,da))
        
        print k, dx, dy, da
        prev = cur.copy()
        #prev = copy.copy(cur)       # maybe deepcopy ?
        prev_grey = copy.copy(cur_grey)
        
        k = k + 1
        
    # Step 2 - Accumulate the transformations to get the image trajectory
    print "=============2================"
    a = x = y = 0
    trajectory = []
    for t in prev_to_cur_transform:
        x += t.dx
        y += t.dy
        a += t.da
        
        trajectory.append(TransformParam(x,y,a))
        
        print x,y,a
        
    # Step 3 - Smooth out the trajectory using an averaging window
    print "=============3================"
    smoothed_trajectory = []
    
    for i,t in enumerate(trajectory):
        sum_x = sum_y = sum_a = 0
        count = 0
            
        for j in xrange(-SMOOTHING_RADIUS,SMOOTHING_RADIUS):
            if ((i+j >= 0) and (i+j < len(trajectory))):
                sum_x += trajectory[i+j].dx
                sum_y += trajectory[i+j].dy
                sum_a += trajectory[i+j].da
                
                count += 1
        
        avg_a = sum_a / count
        avg_x = sum_x / count
        avg_y = sum_y / count
        
        smoothed_trajectory.append(TransformParam(avg_x,avg_y,avg_a))
        print avg_x,avg_y,avg_a
        
    # Step 4 - Generate new set of previous to current transform, such that the trajectory ends up being the same as the smoothed trajectory
    print "=============4================"
    new_prev_to_cur_transform = []
    a = y = x = 0
    
    for i,t in enumerate(prev_to_cur_transform):
        x += t.dx
        y += t.dy
        a += t.da
        
        diff_x = smoothed_trajectory[i].dx - x
        diff_y = smoothed_trajectory[i].dy - y
        diff_a = smoothed_trajectory[i].da - a
        
        dx = t.dx + diff_x
        dy = t.dy + diff_y
        da = t.da + diff_a
        
        new_prev_to_cur_transform.append(TransformParam(dx,dy,da))
        
        print dx,dy,da
        
    # Step 5 - Apply the new transformation to the video
    print "=============5==============="
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
    
    vert_border = HORIZONTAL_BORDER_CROP * prev.shape[0] / prev.shape[1]    # get the aspect ratio correct

    k = 0
    T = numpy.double([[0,0,0],[0,0,0]])
    
    #out = cv2.VideoWriter('output.avi',cv2.cv.FOURCC('Y', 'U', 'V', '9'),59.0,(1280,720),1)
    out = cv2.VideoWriter('output.avi',-1,59.0,(1280,720),1)
    if (out.isOpened() == False):
        print "Error"
        sys.exit()
            
    print "Writing result video"
    while (k < max_frames-1):
        print "{}".format(max_frames-k)
        ret,cur = cap.read()
 
        if ((ret == False) and (cur == None)):
            break
        T[0][0] = math.cos(new_prev_to_cur_transform[k].da)
        T[0][1] = -math.sin(new_prev_to_cur_transform[k].da)
        T[1][0] = math.sin(new_prev_to_cur_transform[k].da)
        T[1][1] = math.cos(new_prev_to_cur_transform[k].da)
        T[0][2] = new_prev_to_cur_transform[k].dx
        T[1][2] = new_prev_to_cur_transform[k].dy
    
        cur2 = cv2.warpAffine(cur,T,cur.shape[0:2])
        
        
        # Resize cur2 back to cur size, for better side by side comparison
        
        # Now draw the original and stablised side by side for coolness
        cv2.imshow("GoProStab",cur2)
        cv2.waitKey(10)
        
        out.write(cur2)
        k += 1

    cv2.destroyAllWindows()
    
    cap.release()
    out.release()
        