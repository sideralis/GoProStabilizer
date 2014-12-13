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
        prev_corner2 = []
        cur_corner2 = []      
        prev_corner = cv2.goodFeaturesToTrack(prev_grey,200,0.01,30)
        cur_corner,status,err = cv2.calcOpticalFlowPyrLK(prev_grey, cur_grey, prev_corner)
        
        # Weed out bad matches
        for st in status:
            if (st == 1):
                # stack
                # prev_corner2.append(prev_corner) 
                pass
        ret = cv2.estimateRigidTransform(prev_corner2, cur_corner2, False)       
        