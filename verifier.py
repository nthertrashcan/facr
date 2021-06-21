import cv2
import numpy as np
import os 
import time
from PIL import Image
import trainer

verbose=True

def initialize(vflag=True):
    global verbose
    verbose=vflag
    faceCascade,recognizer=trainer.initialize()
    wpath=os.getcwd()
    weight=''
    if os.path.isdir(os.path.join(wpath,"model")):
        files=next(os.walk(os.path.join(wpath,"model")))[2]
        for w in sorted(files):
            weight=w
            break

    else:
        weight=trainer.train(faceCascade,recognizer)
    recognizer.read(os.path.join(os.path.join(wpath,"model"),weight))

    return recognizer,faceCascade


def verify(img,cam,recognizer,faceCascade):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,scaleFactor = 1.2,minNeighbors = 5,minSize = (int(0.1*cam.get(3)), int(0.1*cam.get(4))))
    if(faces==()):
        if verbose:
            print("\n [INFO] Unable to detect any face")
        return None
    
    for(x,y,w,h) in faces:
        _, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        if (confidence < 100 and round(100 - confidence)>45 ):
            if verbose:
                print("\n [INFO] Admin")
            return True

    if verbose:
        print("\n [INFO] Unknown")
    return False


# cam = cv2.VideoCapture(0)

# recognizer,faceCascade=initialize()

# while True:
#     rate,frame=cam.read()
#     verify(frame,cam,recognizer,faceCascade)

# cam.release()
# cv2.destroyAllWindows()