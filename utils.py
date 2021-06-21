
import os
import subprocess as sp
from subprocess import PIPE
import time
import sys
import psutil
import logging


verbose=True

def initialize(vflag):
    global verbose
    verbose=vflag
    avoid=[]

    if len(sys.argv)>1 and sys.argv[1]=="-i":
        with open("logs/ignore_path.txt","w") as f:
            path=str("".join(sys.argv[1:])).split("-i")[1]
            if os.path.isfile(os.path.join(path,"ignore.txt")):
                for i in open(os.path.join(path,"ignore.txt"),"r"):
                    avoid.append(i.strip("\n"))
            f.write(f"{path}\n")
    else:
        if os.path.isfile(os.path.join(os.getcwd(),"logs/ignore_path.txt")): 
            with open("logs/ignore_path.txt","r") as f:
                path=f.readlines()[0].rstrip()
                if os.path.isfile(os.path.join(path,"logs/ignore.txt")):
                    for i in open(os.path.join(path,"logs/ignore.txt"),"r"):
                        avoid.append(i.strip("\n"))

    return avoid


def processes(extn,avoid=[]):

    procs={}
    driver={}
    files=[]
    apps=[]
    rapps=[]
    running=[]
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select ProcessName' 

    
    def findx(p):
        if p.name() in ["Microsoft.Photos.exe","Music.UI.exe","Video.UI.exe"]:
            if not p.is_running():
                p.resume()
            if p.open_files():
                for o in p.open_files():
                    if any(o.path.endswith(x) for x in extn):
                        if "C:\\Program Files\\WindowsApps" not in o.path:
                            if o.path not in files and p.name() not in driver.keys():
                                files.append(o.path)
                            procs[(o.path,p.name())]=p                                    
                            driver[p.name()]=o.path

        if p.cmdline():
            for c in p.cmdline():
                if any(c.endswith(x) for x in extn):
                    if c.startswith(p.cwd()[:3]):
                        if c not in files and p.name() not in driver.keys():
                            files.append(c)
                        procs[(c,p.name())]=p
                        # procs[c]=p
                        driver[p.name()]=c
                    else:
                        if os.path.join(p.cwd(),c) not in files and p.name() not in driver.keys():
                            files.append(os.path.join(p.cwd(),c))
                        procs[(os.path.join(p.cwd(),c),p.name())]=p
                        driver[p.name()]=os.path.join(p.cwd(),c)


    proc = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
    for process in proc.stdout:
        running.append(process.decode().rstrip())
    running=running[3:-2]


    for i in running:
        if i not in avoid and i not in rapps:
            rapps.append(i)

    for p in psutil.process_iter(['pid','name']):
        if p.info["name"].split(".",1)[0] in rapps:
            if p.info['name'] not in apps:
                procs[(p.info['name'],"")]=p
                apps.append(p.info['name'])
        try:
            findx(p)
        except:
            pass
    
    return (files,apps,procs,driver)


def suspend(procs,args,extn,flag=True,admin=True):
    if flag:
        _,_,ops=read()
        for op in ops:
            if "suspend" in op[0]:
                if op[1].lower() in args:
                    args.remove(op[1].lower())

    suspended=[]
    for arg in args:
        nflag=True
        arg=arg.lower()
        if any(arg.endswith(ext) for ext in extn):
            for process in procs:
                if process[0].lower()==arg or arg in process[0].lower():
                    if arg!=process[0].lower():
                        arg=process[0]

                    cur=procs[process]
                    try:
                        if verbose:
                            if cur.is_running():
                                if arg not in suspended:
                                    suspended.append(arg)
                                    print("\n [INFO] Suspending {}.".format(arg))
                        for parent in cur.parents():
                            if parent.name()!="explorer.exe" and parent.name()!="cmd.exe":
                                if "py" in parent.name() and parent.name().endswith(".exe"):
                                    pass
                                else:
                                    try:
                                        if parent.is_running():
                                            parent.suspend()
                                    except:
                                        pass
                        for child in cur.children():
                            if child.is_running():
                                child.suspend()
                        if cur.is_running():
                            cur.suspend()
                        if admin:
                            with open("logs/logs.txt","a") as f:
                                f.write(f"o - suspend {process[0]}\n")
                    except:
                        print("\n [ERROR] Process does not exist.")
                    nflag=False  
                    # break    
            if nflag:
                if verbose:
                    print("\n [INFO] Process {} not Found.".format(arg))


def resume(procs,args,extn,flag=True,admin=True):
    if flag:
        args=[]
        files,apps,ops=read()
        fnl_ops=ops.copy()
        for op in ops:
            if "suspend" in op[0]:
                args.append(op[1])
                fnl_ops.remove(op)

        logg(files,apps,fnl_ops,False)

    resumed=[]
    for arg in args:
        nflag=True
        arg=arg.lower()
        if any(arg.endswith(ext) for ext in extn):
            for process in procs:
                if process[0].lower()==arg or arg in process[0].lower():
                    if arg!=process[0].lower():
                        arg=process[0]
                    cur=procs[process]
                    try:
                        if verbose:
                            if arg not in resumed:
                                resumed.append(arg)
                                print("\n [INFO] Resuming {}.".format(arg))
                        for parent in cur.parents():
                            if parent.name()!="explorer.exe" and parent.name()!="cmd.exe":
                                if "py" in parent.name() and parent.name().endswith(".exe"):
                                    pass
                                else:
                                    try:
                                        parent.resume()
                                    except:
                                        pass
                        for child in cur.children():
                            child.resume()
                        
                        cur.resume()
                        nflag=False
                    except:
                        pass
                    # break      
            if nflag:
                if verbose:
                    print("\n [INFO] Resuming {}".format(arg))
                    sp.Popen(arg, shell=True)


def kill(procs,args,extn,flag=True,admin=True):
    if flag:
        files,apps,ops=read()
        for op in ops:
            if "kill" in op[0]:
                if not op[1].endswith(".exe"):
                    op=op[1].split(" ",1)[1].strip().lower()
                else:
                    op=op[1].lower()
                if op in args:
                    args.remove(op)
            
    killed=[]
    for arg in args:
        nflag=True
        arg=arg.lower()
        if any(arg.endswith(ext) for ext in extn):
            for process in procs:
                if process[0].lower()==arg or arg in process[0].lower():
                    if arg!=process[0].lower():
                        arg=process[0]
                    cur=procs[process]
                    try:
                        if verbose:
                            if arg not in killed:
                                killed.append(arg)
                                print("\n [INFO] Killing {}.".format(arg))
                        for parent in cur.parents():
                            if parent.name()!="explorer.exe" and parent.name()!="cmd.exe":
                                if "py" in parent.name() and parent.name().endswith(".exe"):
                                    pass
                                else:
                                    try:
                                        parent.terminate()
                                    except:
                                        pass    
                        for child in cur.children():
                            child.terminate()
                        cur.terminate()
                        if admin:
                            with open("logs/logs.txt","a") as f:
                                f.write("o - kill {}\n".format(process[0]))
                    except:
                        print("\n [ERROR] Process does not exist.")
                    nflag=False
                    # break      
            if nflag:
                if verbose:
                    print("\n [INFO] Process {} not Found.".format(arg))

def revive(procs,args,extn,flag=True,admin=True):
    if verbose:
        print("\n [INFO] Restarting.")
    files,apps,ops=read()
    fnl_files=files.copy()
    fnl_apps=apps.copy()
    fnl_ops=ops.copy()
    kargs=[]
    sargs=[]
    if ops:
        for cmd in ops:
            op=cmd[0]
            arg=cmd[1]
            if op=="suspend":
                sargs.append(arg)
                if cmd in fnl_ops:
                    fnl_ops.remove(cmd)

            if op=="kill":
                if arg not in kargs:
                    kargs.append(arg)
                if cmd in fnl_ops:
                    fnl_ops.remove(cmd)

    if sargs:
        resume(procs,args,extn)

    if kargs:
        for arg in kargs:
            if verbose:
                print("\n [INFO] Opening {}".format(arg))
            sp.Popen(arg, shell=True)

    logg(fnl_files,fnl_apps,fnl_ops,False)


def logg(files,apps,ops=[],flag=True):
    tmp_ops=[]
    check=[]

    if os.path.isfile(os.path.join(os.getcwd(),"logs/logs.txt")):
        _,_,tmp_ops=read()

    with open("logs/logs.txt","w") as f:
        for file in files:
            if file not in check:
                f.write(f"f - {file}\n")
                check.append(file)
            
        for app in apps:
            if app not in check:
                f.write(f"e - {app}\n")
                check.append(app)

        for op in ops:
            if op not in check:
                if op in tmp_ops:
                    tmp_ops.remove(op)
                f.write(f"o - {op[0]} {op[1]}\n")
                check.append(op)

    if flag:
        with open("logs/logs.txt","a") as f:
            for op in tmp_ops:
                if op not in check:
                    f.write(f"o - {op[0]} {op[1]}\n")
                    check.append(op)

def read():
    ops=[]
    files=[]
    apps=[]
    with open("logs/logs.txt",'r') as f:
        for cmd in f.readlines():
            cmd=cmd.split('-',1)
            cmd[0]=cmd[0].strip()
            if cmd[0]=='o':
                cmd=cmd[1]
                cmd=cmd.strip()
                ops.append(cmd.split(" ",1))
            elif cmd[0]=='f':
                cmd=cmd[1]
                cmd=cmd.strip()
                files.append(cmd)
            elif cmd[0]=='e':
                cmd=cmd[1]
                cmd=cmd.strip()
                apps.append(cmd)
    
    return files,apps,ops

def remfromignorelist(arg):
    procs=[]
    path=os.getcwd()
    if os.path.isfile(os.path.join(os.getcwd(),"logs/ignore_path.txt")):
        with open(os.path.join(os.getcwd(),"logs/ignore_path.txt"),'r') as f:
            path=osos.path.join(path,f.readlines()[0].strip())
    else:
        path=os.path.join(path,"logs")


    with open(os.path.join(path,"ignore.txt"),"r") as f:
        for cmd in f.readlines():
            cmd.replace("\\","\\")
            cmd=cmd.strip()
            if cmd.lower()!=arg.lower():
                procs.append(cmd)
            else:
                print("\n [INFO] Removing {} from ignore list.".format(arg))

    with open(os.path.join(path,"ignore.txt"),"w") as f:
        for cmd in procs:
            f.write(f"{cmd}\n")


def addtoignorelist(arg):
    path=os.getcwd()
    if os.path.isfile(os.path.join(os.getcwd(),"logs/ignore_path.txt")):
        with open(os.path.join(os.getcwd(),"logs/ignore_path.txt"),'r') as f:
            path=osos.path.join(path,f.readlines()[0].strip())
    else:
        path=os.path.join(path,"logs")

    if arg!="":
        print("\n [INFO] Adding {} to ignore list.".format(arg))
        with open(os.path.join(path,"ignore.txt"),"a") as f:
            f.write(f"{arg}\n")
    else:
        print("\n [ERROR] No argument given.")

def rn_status(admin=True):
    with open(os.path.join(os.getcwd(),"logs/driver.txt"),"w") as f:
        if admin:
            f.write("1")
        else:
            f.write("0")







# def terminate(procs):
#     print("\n [INFO] Terminating.")
#     for process in procs:
#         procs[process].terminate()


# extn=['.mp3','.rar','.zip','.gz','.png','.jpeg','.mp4','.mkv','.docx','.py','.pdf']
# import sys

# if len(sys.argv)>1:
#     avoid=initialize(1)
#     files,apps,procs,driver=processes(extn,avoid)
    # print(files)
    # print(apps)
    # print(procs.keys())
    # # for i in procs:
    # #     print(i)
    # print(driver.keys())
    # # logg(files,apps)

    # if sys.argv[1]=="-r":
    #     for i in driver:
    #         for arg in sys.argv[2:]:
    #             if arg in driver[i]:
    #                 resume(procs,[driver[i]],extn)
    # elif sys.argv[1]=="-s":
    #     for i in driver:
    #         for arg in sys.argv[2:]:
    #             if arg in driver[i]:
    #                 suspend(procs,[driver[i]],extn)
            # if sys.argv[2] in driver[i]:
            #     suspend(procs,[driver[i]],extn)
    # elif sys.argv[1]=="-k":
    #     for i in driver:
    #         for arg in sys.argv[2:]:
    #             if arg in driver[i]:
    #                 kill(procs,[driver[i]],extn,0)
#     elif sys.argv[1]=="-a":
#         addtoignorelist(sys.argv[2])
#     elif sys.argv[1]=="-rm":
#         remfromignorelist(sys.argv[2])
    # elif sys.argv[1]=="-rv":
    #     revive(procs,[],extn)
        # revive(procs)
# else:
#     pass

