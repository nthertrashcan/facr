import getpass
import os
import subprocess as sp
from subprocess import PIPE
import time
import sys
import psutil
import utils
import shutil


def initialize():
	profile=''
	proc=None
	avoid=utils.initialize()
	_,_,_,procs=utils.processes(ext,avoid)
	for i in procs:
		if "chrome.exe" in procs[i].name():
			proc=procs[i]
			for c in procs[i].parents():
				if len(c.cmdline())>1:
					profile=c.cmdline()[1].split("=",1)[1].strip()
					break
			break
	return profile,proc

def terminate(proc):
	for parent in proc.parents():
		if parent.name()!="explorer.exe":
			parent.terminate()
	for child in proc.children():
		child.terminate()

def chrome(username,profile,proc,flag=False):
	if proc:
		if flag:
			terminate(proc)

		src=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}/Sessions'
		dest=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}/facr_cache'

		if os.path.isdir(src):
			time.sleep(2)
			print("\n [INFO] Collecting session cache.")
			if not os.path.isdir(dest):
				os.mkdir(dest)
			if os.path.isdir(os.path.join(dest,"Sessions")):
				shutil.rmtree(os.path.join(dest,"Sessions"))
			shutil.move(src,dest,copy_function=shutil.copytree)

def chromert(username,profile,proc,flag=False):
	if proc:
		if flag:
			terminate(proc)

		src=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}/facr_cache/Sessions'
		dest=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}/'
		

		if os.path.isdir(src):
			time.sleep(2)
			print("\n [INFO] Retrieving session cache.")
			if os.path.isdir(os.path.join(dest,"Sessions")):
				shutil.rmtree(os.path.join(dest,"Sessions"))
			shutil.move(src,dest,copy_function=shutil.copytree)

    

def his(username,profile,proc,flag=False):
	if proc:
		if flag:
			terminate(proc)
		files=["History","History Provider Cache","History-journal"]
		print("\n [INFO] Collecting history cache.")
		for f in files: 
			src=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}/{f}'
			dest=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}/facr_cache'
			if os.path.isfile(src):
				time.sleep(2)
				
				if not os.path.isdir(dest):
					os.mkdir(dest)
				if os.path.isfile(os.path.join(dest,f"{f}")):
					shutil.rmtree(os.path.join(dest,f"{f}"))
				shutil.move(src,dest,copy_function=shutil.copytree)	

def hisrt(username,profile,proc,flag=False):
	if proc:
		if flag:
			terminate(proc)

		files=["History","History Provider Cache","History-journal"]
		print("\n [INFO] Retrieving history cache.")
		for f in files:
			src=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}/facr_cache/{f}'
			dest=f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/{profile}'
			if os.path.isfile(src):
				time.sleep(2)
				
				if os.path.isfile(os.path.join(dest,f"{f}")):
					os.remove(os.path.join(dest,f"{f}"))
				shutil.move(src,dest)


# username=getpass.getuser()
# profile,proc=initialize()

# import sys

# if len(sys.argv)>1:
# 	if sys.argv[1]=="-c":
# 		chrome(username,profile,proc,True)
# 	elif sys.argv[1]=="-crt":
# 		chromert(username,profile,proc,True)
# 	elif sys.argv[1]=="-h":
# 		his(username,profile,proc,True)
# 	elif sys.argv[1]=="-hrt":
# 		hisrt(username,profile,proc,True)
# 	elif sys.argv[1]=="-f":
# 		chrome(username,profile,proc,True)
# 		his(username,profile,proc)
# 	elif sys.argv[1]=="-frt":
# 		chromert(username,profile,proc,True)
# 		hisrt(username,profile,proc)

