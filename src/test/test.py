'''
Created on 2017��4��12��

@author: Cloudsoar
'''

if __name__ == '__main__':
    pass


1��ͨ��paramiko��sshģ������ָ��������
 
2) ͨ��SSHClient.exec_command��Զ��������ִ�����
 
3��ͨ��exec_command���ص�stdout,stdin,stderr���н�����
 
4������ɹ����ӵ�������Ϣ��session��������ͨ��ls����鿴�� session id���ֱ�����������ӣ�
 
5������windows��linux�����У�д����ʱ��Ҫע�����ǵĲ��
����ssh.py
 
#!/usr/bin/python
# -*- coding: utf-8 -*-
  
import os,sys
import paramiko  
import threading  
import platform
  
curr_ssh = None 
curr_prompt = ">>"
  
#ʹ��˵��       
def printUsage():
    print "    !ls                     :list sessions."
    print "    !session id             :connect session."
    print "    !conn host user password:connect host with user."
    print "    !exit                   :exit."
  
#���� 
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
          
#������ǰ��������Ϣ
sessions=[]
def loadSessions():
    global sessions
    try:
        f = open("sessions")
        sessions = f.readlines()
        f.close()
    except:
        pass
  
#ִ�б�������,ssh.py������       
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
                    sessions[id]="" os.system(new_console_cmd)="" else:="" print="" "didn't="" hava="" sessoin="" ",vals[1]="" elif(vals[0]="="!conn"):" global="" curr_ssh="" f="open("sessions","a")" line="vals[1]+"" "+vals[2]+"="" "+vals[3]+"\n"="" f.write(line)="" f.close()="" #��ssh���ӵ�������ִ������="" def="" exe_cmd_ssh(ssh,cmd):="" if(ssh="=" none):="" connect="" to="" a="" server.="" use="" '!conn'="" please."="" return="" stdin,="" stdout,="" stderr="ssh.exec_command(cmd)" #stdin.write("y")="" #�򵥽���������="" ��y��="" #��Ļ���="" stdout.read()="" stderr.read()="" #��ں���="" if="" __name__="='__main__':" loadsessions()="" if(len(sys.argv)="=4):" printusage()="" while="" true:="" cmd="raw_input(curr_prompt)" if(len(cmd)="=0):" continue="" if(cmd="=" "!exit"):="" if(curr_ssh="" !="None):" curr_ssh.close();="" break="" if(cmd[0]="=" '!'):="" exe_cmd_local(cmd)="" exe_cmd_ssh(curr_ssh,cmd)<="" pre="">