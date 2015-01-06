'''
Created on 20 nov. 2014

@author: Bernard
'''
import cv2
import numpy
import math
import copy

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
        prev = copy.copy(cur)       # maybe deepcopy ?
        prev_grey = copy.copy(cur_grey)
        
        k = k + 1
        
    # Step 2 - Accumulate the transformations to get the image trajectory
    pass
        
        
        
        
        
        