import cv2
import numpy as np
import os 
import time
from PIL import Image
import sys
from collections import defaultdict


# root=os.getcwd()

def initialize():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
    path=''
    mode='a'
    paths=defaultdict(list)
    if not os.path.isfile(os.path.join(os.getcwd(),"logs/paths.txt")):
        mode='w'
    else:
        with open(os.path.join(os.getcwd(),"logs/paths.txt"),'r') as f:
            for path in f.readlines():
                paths[path.split("-")[0].strip()].append(path.split("-")[1].strip())

    if len(sys.argv)>1:
        if sys.argv[1]=="-t":
            if len(sys.argv)>2:
                path=sys.argv[2]
            else:
                path=os.getcwd()
    else:
        path=os.getcwd()



    if mode=='a':
        if "d" in paths:
            if path in paths["d"]:
                return face_detector,recognizer
            else:

                paths["d"].clear()
                # print(path)
                if "-" in path:
                    paths["d"].append(path.split("-")[1].strip())
                else:
                    paths["d"].append(path)


    with open(os.path.join(os.getcwd(),"logs/paths.txt"),'w') as f:
        if paths:
            for path in paths:
                for p in paths[path]:
                    f.write("{} - {}\n".format(path,p))
        else:
            if path=='':
                path=os.getcwd()
            f.write("d - {}\n".format(path))

    return face_detector,recognizer


def capture(face_detector):
    root=os.getcwd()

    if "-t" in sys.argv:
        indx=sys.argv.index("-t")
        root=" ".join(sys.argv[indx+1:indx+2])
        
    if os.path.isdir(os.path.join(root,"dataset")):
        pass
    else:
        print("\n [INFO] Dataset directory created.")
        os.mkdir(os.path.join(root,"dataset"))


    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480) 
    face_id = int(input('\n [INPUT] Enter user id -: '))
    ns = input("\n [INPUT] Enter number of samples -: ")
    count=0

    if ns=="":
        ns=500
    else:
        ns=int(ns) 

    print("\n [INFO] Look the camera and wait ...")
    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1
            cv2.imwrite(os.path.join(root,"dataset")+"/User." + str(face_id) + '.' +  
                        str(count) + ".jpg", gray[y:y+h,x:x+w])
            cv2.imshow('', img)
         
        if cv2.waitKey(1) == ord('q'):
            break
        elif count >= ns:
             break
    print("\n [INFO] Capturing complete!!!")
    cam.release()
    cv2.destroyAllWindows()



def train(face_detector,recognizer,grayscale=True):
    root=os.getcwd()
    wpath=os.getcwd()
    if os.path.isfile(os.path.join(os.getcwd(),"logs/paths.txt")):
        with open(os.path.join(os.getcwd(),"logs/paths.txt"),"r") as f:
            for path in f.readlines():
                if path.split("-")[0].strip()=='d':
                    root=path.split("-")[1].strip()
                elif path.split("-")[0].strip()=='w':
                    wpath=path.split("-")[1].strip()

    if not os.path.isdir(os.path.join(root,"dataset")):
        capture(face_detector)
    if not os.path.isdir(os.path.join(wpath,"model")):
        os.mkdir(os.path.join(wpath,"model"))
        print("\n [INFO] Trainer directory created.")

    path = os.path.join(root,"dataset")
    def getImagesAndLabels(path):
        imagePaths = [f for f in os.listdir(path)]     
        faceSamples=[]
        ids = []
        for imagePath in imagePaths:
            if grayscale:
                PIL_img = Image.open(os.path.join(path,imagePath)).convert('L')
            else:
                PIL_img = Image.open(os.path.join(path,imagePath))

            img_numpy = np.array(PIL_img,'uint8')
            idx = int(os.path.split(imagePath)[-1].split(".")[1])
            
            faces = face_detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(idx)
        return faceSamples,ids

    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))
    uid=str(time.time()).replace(".","")
    recognizer.write(os.path.join(os.path.join(wpath,"model"),f"weights{uid}.yml"))

    print("\n [INFO] Training completed!!!".format(len(np.unique(ids))))
    return f"weights{uid}.yml"



# face_detector,recognizer=initialize()


# if len(sys.argv)>1:
#     if sys.argv[1]=='-c':
#         capture(face_detector)
#     elif sys.argv[1]=='-t':
#         trainer(face_detector,recognizer)

# trainer()