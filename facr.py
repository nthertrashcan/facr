import os 
import sys
import numpy as np
import subprocess as sp
import psutil
import getpass
from PIL import Image
import cv2
import time
import datetime
import analyze
import utils 
import verifier
import trainer
from extras import chromeutil


def init():
	if not os.path.isdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs")):
		os.mkdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs"))

	files=["cmd.txt","driver.txt","ignore.txt","ignore_path.txt","klist.txt","logs.txt","paths.txt","slist.txt"]

	for file in files:
		if not os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs/{}".format(file))):
			f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs/{}".format(file)),"w")

init()


def facr(verbose=True):
	admin=True
	flag=1

	flist,op,listpath,extn=analyze.initialize(verbose)
	avoid=utils.initialize(verbose)
	recognizer,faceCascade=verifier.initialize(verbose)

	cam = cv2.VideoCapture(0)
	adminlist=[]
	admindriver={}
	while True:
		flist,procs,driver=analyze.dlist(flist,op,listpath,extn,avoid)
		rate,frame=cam.read()
		check=verifier.verify(frame,cam,recognizer,faceCascade)
		
		if check:
			utils.rn_status()
		else:
			utils.rn_status(admin)

		if flag==0:
			if not check:
				analyze.unknown(op,flist,procs,extn)
				flag=1
			else:
				adminlist=flist
				admindriver=driver	

		elif flag==1:
			if not adminlist:
				adminlist=flist
				admindriver=driver
			
			if check:
				analyze.admin(op,flist,procs,extn)
				flist,procs,driver=analyze.dlist(flist,op,listpath,extn,avoid)
				if adminlist!=flist:
					tmp=analyze.unmatched(admindriver,adminlist,flist.copy())
					if tmp is None:
						print("\n [INFO] Reviving closed ones.")
						analyze.admin("-k",flist,procs,extn)
					else:
						print("\n [INFO] Killing unknowns.")
						analyze.unknown("-k",tmp,procs,extn,admin=False)
				flag=0
			else:
				analyze.unknown(op,flist,procs,extn)
		
		flist=[]
		driver={}
	cam.release()
	cv2.destroyAllWindows()

def help():
	print(" Usage[%facr% OPTIONS NAME ARG FLAG]\n\
		OPTIONS:\n\
		-s\tSuspend\n \
		-sa\tAppend to Suspend List\n \
		-k\tKill\n \
		-ka\tAppend to Kill List\n \
		-t\tTraining Dataset Path\n \
		-i\tIgnore List Path\n \
		-a\tAdd to ignoe list\n \
		-rm\tRemove from ignore list \n\n \
		NAME: Files(with path) or Apps\n\n\
		ARG:\n\
		-e\t Force extensions \n \
		-v\t Set Verbose False \n \
		")


if not os.path.isdir(os.path.join(os.getcwd(),"model")):
	faceCascade,recognizer=trainer.initialize()
	trainer.train(faceCascade,recognizer)


if len(sys.argv)>1:
	if sys.argv[1]=="-h":
		help()
	elif sys.argv[1]=="-t":
		faceCascade,recognizer=trainer.initialize()
		trainer.train(faceCascade,recognizer)
	elif sys.argv[1]=="-i":
		utils.initialize()
	elif sys.argv[1]=="-a":
		utils.addtoignorelist(sys.argv[2])
	elif sys.argv[1]=="-rm":
		utils.remfromignorelist(sys.argv[2])
	elif "-v" in sys.argv:
		facr(verbose=False)
	else:
		facr()
else:
	facr()