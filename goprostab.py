'''
Created on 20 nov. 2014

@author: Bernard
'''
import cv2
import numpy



if __name__ == '__main__':
    cap = cv2.VideoCapture(r'D:\Users\Bernard\Documents\My Projects\GoPro\GOPR5789.MP4')
#    cap = cv2.VideoCapture(r'D:\Users\Bernard\Videos\chuck s03\chuck.301.vostf.avi')
    assert(cap.isOpened())
        
    ret,prev = cap.read()
    prev_grey = cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY)
    
    # Step 1
    k = 1
    max_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    while(True):
        ret,cur = cap.read()
        if (cur.data == None):
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
        cur_corner2 = cur_corner2.astype(numpy.int)
        prev_corner2 = prev_corner2.astype(numpy.int)
        ret = cv2.estimateRigidTransform(prev_corner2, cur_corner2, False)  
        print ret     
        