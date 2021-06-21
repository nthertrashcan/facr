import psutil
import os
import sys
import subprocess as sp
import time

flag=0
file="facr.py"

if len(sys.argv)>1:
	argv=sys.argv[1:]
else:
	if os.path.isfile(os.path.join(os.getcwd(),"logs/cmd.txt")):
		with open(os.path.join(os.getcwd(),"logs/cmd.txt"),"r") as f:
			argv=f.readlines()[0].split(" ")
cmd=os.path.join(os.getcwd(),file+" "+" ".join(argv))
while True:
	pyfiles=[]
	for p in psutil.process_iter(['pid','name',"cmdline","cwd"]):
			if "python" in p.info["name"]:
				pyfiles.append(p.info['cmdline'][1])
	if os.path.isfile(os.path.join(os.getcwd(),"logs/driver.txt")):
		with open(os.path.join(os.getcwd(),"logs/driver.txt"),'r') as f:
			if not int(f.read()):
				if file not in pyfiles:
					if os.path.isfile(os.path.join(os.getcwd(),"logs/cmd.txt")):
						with open(os.path.join(os.getcwd(),"logs/cmd.txt"),"r") as r:
							argv=r.readlines()[0].split(" ")
							cmd=file+" "+" ".join(argv)

					sp.Popen(f"start /wait cmd /k py {cmd}",shell=True)
					time.sleep(1)
	else:
		sp.Popen(f"start /wait cmd /k py {cmd}",shell=True)
		time.sleep(1)
		with open(os.path.join(os.getcwd(),"logs/driver.txt"),'w') as f:
			f.write("1")
	
