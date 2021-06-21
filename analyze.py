import os 
import sys
import numpy as np
import subprocess as sp
import psutil
import getpass
from PIL import Image
import verifier
import utils 
import cv2
import time
import datetime


verbose=True

def initialize(vflag):
	flist=[]
	argv=sys.argv
	default='-s'
	cmd='-s'
	extn=[".exe",".py",".pyw",".java",".c",".cpp",".h",".txt",".pdf",".docx",".doc",".wav",".mp3",".mkv",".mp4",".jpeg",".png",".jpg",".zip",".rar"]
	path=os.getcwd()
	if len(argv)>1:
		flist,path=writelist(argv[1],argv,path)
		default=argv[1][0:2]
		cmd=argv[1]+" "+" ".join(flist)
	else:
		if checkrestart():
			if os.path.isfile(os.path.join(os.getcwd(),"logs/cmd.txt")):
				with open(os.path.join(os.getcwd(),"logs/cmd.txt"),"r") as f:
					argv=[sys.argv[0]]+f.readlines()[0].split(" ")
		flist,path=writelist(default,argv+[default],path)

	if "-e" in argv:
		path=None
		ind=argv.index("-e")
		extn=argv[ind+1:]
		cmd+="-e "+" ".join(extn)
		for n,ext in enumerate(extn):
			if not ext.startswith("."):
				extn[n]="."+ext

	if len(argv)>1:
		with open(os.path.join(os.getcwd(),"logs/cmd.txt"),"w") as f:
			f.write("{}".format(cmd))

	return flist,default,path,extn


def writelist(arg,argv,path):
	flist=[]
	files={"-s":"slist","-sa":"slist","-k":"klist","-ka":"klist"}
	file_name=files[arg]+".txt"
	if argv[-1]==arg:
			if os.path.isfile(os.path.join(path,"logs/{}".format(file_name))):
				with open(os.path.join(path,"logs/{}".format(file_name)),"r") as f:
					for l in f.readlines():
						flist.append(l.strip())
			else:
				print("\n [ERROR] No list file exist in the given directory.")

	elif argv[1]==arg:

		if os.path.isdir(argv[2]):
			if os.path.isfile(os.path.join(argv[2],"logs/{}".format(file_name))):
				with open(os.path.join(argv[2],"logs/{}".format(file_name)),"r") as f:
					for l in f.readlines():
						flist.append(l.rstrip())
				path=argv[2]
			else:
				print("\n [ERROR] No list file exist in the given directory, Using default {}.".format(path))

		elif os.path.isdir(os.path.join(path,argv[2])):
			if os.path.isfile(os.path.join(path,os.path.join(argv[2],"logs/{}".format(file_name)))):
				with open(os.path.join(path,os.path.join(argv[2],"logs/{}".format(file_name))),"r") as f:
					for l in f.readlines():
						flist.append(l.rstrip())
				path=os.path.join(path,argv[2])		
			else:
				print("\n [ERROR] No list file exist in the given directory, Using default {}.".format(path))
		
		else:
			if "-e" in argv:
				ind=argv.index("-e")
				argv=argv[:ind]
			mode='w'

			if argv[1]=="-sa" or argv[1]=="-ka":
				mode='a'
			if mode=='a':
				with open(os.path.join(path,"logs/{}".format(file_name)),'r') as f:
					for l in f.readlines():
						flist.append(l.rstrip())
			with open(os.path.join(path,"logs/{}".format(file_name)),mode) as f:
				for l in argv[2:]:
					if l not in flist:
						f.write(f"{l}\n")
						flist.append(l)
	return flist,path


def readlist(arg,path):
	flist=[]
	files={"-s":"slist","-sa":"slist","-k":"klist","-ka":"klist"}
	file_name=files[arg]+".txt"
	mode='w'
	if arg=="-s" or arg=="-k":
		mode='a'
	if mode=='a':
		with open(os.path.join(path,"logs/{}".format(file_name)),'r') as f:
			for l in f.readlines():
				flist.append(l.rstrip())
	return flist

def admin(op,flist,procs,extn,flag=True,admin=True):
	ops={"-s":utils.resume,"-k":utils.revive}
	ops[op](procs,flist,extn,flag,admin)

def unknown(op,flist,procs,extn,flag=True,admin=True):
	ops={"-s":utils.suspend,"-k":utils.kill}
	ops[op](procs,flist,extn,flag,admin)

def dlist(flist,op,listpath,extn,avoid):
	driver={}
	files,apps,procs,driver=utils.processes(extn,avoid)
	utils.logg(files,apps)
	if listpath is None:
		flist=files+apps

	elif not flist:
		listpath=os.getcwd()
		flist=readlist(op,listpath)

	if flist:
		for n,fl in enumerate(flist):
			flist[n]=fl.lower()

	return flist,procs,driver

def unmatched(driver,adminlist,flist):
	if len(adminlist)>len(flist):
		tmp=list(set(adminlist).intersection(flist))
		for t in tmp:
			adminlist.remove(t)
		if os.path.isfile(os.path.join(os.getcwd(),"logs/logs.txt")):
			with open(os.path.join(os.getcwd(),"logs/logs.txt"),"a") as f:
				for arg in adminlist:
					f.write("o - kill {}\n".format(arg))
		return None

	else:
		tmp=list(set(flist).intersection(adminlist))
		for t in tmp:
			flist.remove(t)

		return flist

def checkrestart():
	if 1000.>time.time()-psutil.boot_time():
		return True
	else:
		return False
