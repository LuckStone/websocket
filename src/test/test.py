'''
Created on 2017年4月12日

@author: Cloudsoar
'''

if __name__ == '__main__':
    pass


1）通过paramiko的ssh模块连接指定主机；
 
2) 通过SSHClient.exec_command在远程主机上执行命令；
 
3）通过exec_command返回的stdout,stdin,stderr进行交互；
 
4）保存成功连接的主机信息（session），可以通过ls命令查看， session id命令，直接启动新连接；
 
5）可在windows和linux下运行，写程序时需要注意他们的差别。
代码ssh.py
 
#!/usr/bin/python
# -*- coding: utf-8 -*-
  
import os,sys
import paramiko  
import threading  
import platform
  
curr_ssh = None 
curr_prompt = ">>"
  
#使用说明       
def printUsage():
    print "    !ls                     :list sessions."
    print "    !session id             :connect session."
    print "    !conn host user password:connect host with user."
    print "    !exit                   :exit."
  
#连接 
def conn(ip,username,passwd):
    try:
        ssh = paramiko.SSHClient()  
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        ssh.connect(ip,22,username,passwd,timeout=5)  
        print "Connect to ",ip," with ",username
        global curr_prompt
        curr_prompt=username+"@"+ip+">>"
        return ssh
    except:
        return None
          
#加载以前的连接信息
sessions=[]
def loadSessions():
    global sessions
    try:
        f = open("sessions")
        sessions = f.readlines()
        f.close()
    except:
        pass
  
#执行本地命令,ssh.py的命令       
def exe_cmd_local(cmd):
    if(cmd == "!ls"):
        loadSessions()
        global sessions
        i=0
        print "Sessions:"
        for s in sessions:
            print"[%d] %s" %(i,s)
            i+=1
    else:
        vals = cmd.split(' ')
        if(vals[0]=="!session"):
            id = (int)(vals[1])
             if(id<len(sessions)): 
                 os_name=platform.system() 
                 new_console_cmd="" 
                 if(os_name == "linux"):
                     ssh.py="" "="" +="" sessions[id]+"\""="" 
                elif(os_name="=" "windows"):
                    sessions[id]="" os.system(new_console_cmd)="" else:="" print="" "didn't="" hava="" sessoin="" ",vals[1]="" elif(vals[0]="="!conn"):" global="" curr_ssh="" f="open("sessions","a")" line="vals[1]+"" "+vals[2]+"="" "+vals[3]+"\n"="" f.write(line)="" f.close()="" #在ssh连接的主机上执行命令="" def="" exe_cmd_ssh(ssh,cmd):="" if(ssh="=" none):="" connect="" to="" a="" server.="" use="" '!conn'="" please."="" return="" stdin,="" stdout,="" stderr="ssh.exec_command(cmd)" #stdin.write("y")="" #简单交互，输入="" ‘y’="" #屏幕输出="" stdout.read()="" stderr.read()="" #入口函数="" if="" __name__="='__main__':" loadsessions()="" if(len(sys.argv)="=4):" printusage()="" while="" true:="" cmd="raw_input(curr_prompt)" if(len(cmd)="=0):" continue="" if(cmd="=" "!exit"):="" if(curr_ssh="" !="None):" curr_ssh.close();="" break="" if(cmd[0]="=" '!'):="" exe_cmd_local(cmd)="" exe_cmd_ssh(curr_ssh,cmd)<="" pre="">