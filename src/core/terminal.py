# -*- coding: utf-8 -*-
'''
Created on 2017年4月11日

@author: Cloudsoar
'''
import StringIO
import json
import platform
import re
import select
import socket
import threading
import time

import paramiko
from paramiko.py3compat import u
from twisted.internet.protocol import Protocol
from txsockjs.utils import normalize

from common.util import Result
from frame.logger import Log, PrintStack


class Shell(threading.Thread):
    def __init__(self, transport, chanel, interval=0.5):
        super(Shell, self).__init__(name='Shell')
        self.interval=interval
        self.transport = transport
        self.chanel = chanel
        self.send_2_client = False
        self.logined = False
        self.root_prompt = None
        self.match_kube_cmd = False
        self.setDaemon(True)
        self.num = 0
        self.expiry_time = 0

    def run(self):
        while True:
            self.num += 1

            if not self.timeout():
                break
            time.sleep(self.interval)
        Log(4, "Shell end......")

    def is_login(self):
        Log(4, "is_login self.interval:{}, self.logined:{}".format(self.interval, self.logined))
        return self.logined

    def logout(self):
        Log(3, "chan is being logout")
        self.logined = False

    def parse_root_prompt(self, message):
        if self.root_prompt:
            return
        arr = message.split('\r\n')
        for line in arr:
            if len(line) > 3 and line[-2:] == '# ':
                self.root_prompt = line
                break
            
    def parse_user_prompt(self, message):
        Log(3, 'parse_user_prompt in:[%s]'%(message))
        if not self.match_kube_cmd:
            return
        
        arr = message.split('\r\n')
        Log(3, 'parse_user_prompt arr:[%s]'%(str(arr)))
        for line in arr:
            if len(line) >= 2 and line[-2:] == '# ':
                self.logined = True
                break
              
    def sent(self, message, encoding="cp1252"):
        Log(3, 'Shell return:[%s]'%(message))
        if message[0] == '[':
            return
        
        if not self.logined:
            self.parse_root_prompt(message)
            m1 = re.search(r'~# kubectl exec .+\r\n(.*)', message)
            m2 = re.search(r'# kubectl exec .+\r\n(.*)', message)
            if m1 or m2:
                self.match_kube_cmd = True
                self.logined = True

            return

        else:
            if self.root_prompt and message.rfind(self.root_prompt) != -1:
                Log(3, "self.logined is seted false")
                self.logined = False
                return
            
        message = normalize(message, encoding)
        json_msg = 'a{0}'.format(json.dumps([message], separators=(',',':')))

        if getattr(self.transport, "writeRaw", None) is not None:
            self.transport.writeRaw(json_msg)
        else:
            self.transport.write(message)
            
    def timeout(self):
        pass

class WindowsShell(Shell):

    def timeout(self):
        try:
            data = u(self.chanel.recv(2048))
            if data:
                self.sent(data)
                return True
            else:
                return False
        except socket.timeout:
            Log(3, "windows shell socket.timeout")
            self.sent('\r\n**** EOF\r\n')
            self.chanel.close()
            return False
        except Exception, e:
            Log(3, "WindowsShell error:{}".format(e.message))
            PrintStack()
            return False
            

class LinuxShell(Shell):
    
    def timeout(self):
        try:
            r, _, e = select.select([self.chanel], [], [self.chanel])
            if self.chanel in r:
                data = u(self.chanel.recv(2048))
                if len(data) == 0:
                    self.sent('\r\n*** EOF\r\n')
                    return False
                else:
                    self.sent(data)
                    return True
            return False
        except socket.timeout:
            Log(3, "linux shell socket.timeout")
            self.sent('\r\n**** EOF\r\n')
            return False
        except Exception as e:
            Log(3, "LinuxShell error:{}".format(e.message))
            PrintStack()
            return False

def get_ssh_param(key):
    return {
        'ip':'192.168.16.131',
        'port':22,
        'username':'root',
        'password':'123456',
        'pod':'wordpress-gpzwzzgzul-114727340-hxv5z',
        'namespace':'workspacex',
        'container':'wordpress-gpzwzzgzul',
        'bash':'/bin/sh'
    }


    
# def get_ssh_param(key):
#     return {
#         'ip':'192.168.14.166',
#         'port':22,
#         'username':'root',
#         'password':'123456',
#         'pod':'ufleet-project-3286261207-xlh04',
#         'namespace':'ufleet',
#         'container':'ufleet-store',
#         'bash':'/bin/bash'
#     }
        

class SSHChanel(object):
    def __init__(self):
        pass
        
    def parse_param(self, conn):
        try:
            data = get_ssh_param(conn)
            self.ip = data.get('ip', '')
            self.port = data.get('port', 22)
            self.username = data.get('username', '')
            self.password = data.get('password', '')
            self.prikey = data.get('prikey', '')
            self.prikeypwd = data.get('prikeypwd', '')
            self.pod = data.get('pod', '')
            self.namespace = data.get('namespace', '')
            self.container = data.get('container', '')
            self.bash = data.get('bash', '/bin/sh')
            # 连接失败重试的次数
            self.try_times = 3
            self.transe = None
            return Result(0)
        except Exception as e:
            Log(1, "sshchanle error:{}".format(e.message))
            return Result('', 400, e.message)

    def connect(self):
        while True:
            try:
                if self.prikey:
                    not_really_a_file = StringIO.StringIO(self.prikey)
                    private_key = paramiko.RSAKey.from_private_key(not_really_a_file, self.prikeypwd)
                    not_really_a_file.close()
                else:
                    private_key = None

                self.transe = paramiko.Transport(sock=(self.ip, self.port))
                self.transe.connect(username=self.username, password=self.password, pkey=private_key)

                chan = self.transe.open_session(timeout=20)
                chan.settimeout(30)
                chan.get_pty(width=400)
                chan.invoke_shell()
                return True, chan
            except Exception, e:
                Log(1, 'transe connect error:{}'.format(e.message))
                # PrintStack()
                if self.try_times != 0:
                    self.try_times -= 1
                else:
                    return None, e.message

    def login(self, transport, conn):
        rlt = self.parse_param(conn)
        if not rlt.success:
            return rlt
        c_status, self.chanel = self.connect()
        if c_status is None:
            Log(3, "login:{}".format(self.chanel))
            return Result('', 400, self.chanel)

        self.receive(transport, self.chanel)
        self._send_cmd('\r')
        self._send_cmd('kubectl exec -it %s --namespace=%s -c %s -- %s\r' % (self.pod, self.namespace, self.container, self.bash))
        Log(4, "send cmd:kubectl exec -it %s --namespace=%s -c %s -- %s\r" % (self.pod, self.namespace, self.container, self.bash))
        return Result(0)

    # 判断用户所使用的操作系统
    def receive(self, transport, chan):
        os_name = platform.system()
        Log(3, "os_name:{}".format(os_name))
        if os_name == "Linux":
            self.shell = LinuxShell(transport, chan, 0.2)
        else:
            self.shell = WindowsShell(transport, chan, 0.2)

        self.shell.start()

    def _send_cmd(self, cmd):
        # cmd += '\r'
        self.chanel.send(cmd)

    def send_cmd(self, cmd):
        if self.shell.is_login():
            self._send_cmd(cmd)
        else:
            raise LogoutException('The session is close')

    def close(self):
        if hasattr(self, 'shell'):
            Log(3,
                "chanel.close started shell:{}, transe:{}".format(self.shell.isAlive(), self.transe.isAlive()))
        # self.chanel.close()
        if hasattr(self, 'transe'):
            if self.transe:
                self.transe.stop_thread()
        if hasattr(self, 'shell'):
            Log(3, "chanel.close status shell:{}, transe:{}".format(self.shell.isAlive(), self.transe.isAlive()))


class LogoutException(Exception):
    def __init__(self, value, errid=1):
        self.value = value
        self.errid = errid

    def __str__(self):
        return repr(self.value)


# 前端页面终端和后台
class SSHProtocol(Protocol):
    
    def connectionMade(self):
        self.sent('------hello----------')

    # 通过chanel向主机发送命令
    def exec_command(self, cmd):
        try:
            self.transport.chanel.send_cmd(cmd)
        except LogoutException as e:
            Log(3, "logout exception....:{}".format(str(e)))
            self.transport.chanel.close()
            self.transport.loseConnection()
        except Exception, e:
            Log(1, 'SSHProtocol exec_command  except [%s]' % e.message)

    def add_chanel(self, data):
        """
        :param data:
        :return:
        """
        sshchan = SSHChanel()
        rlt = sshchan.login(self.transport, data)
        if not rlt.success:
            Log(1, "terminal login failed. error:{}".format(rlt.message))
            self.sent('\r')
            self.sent(rlt.message)
            sshchan.close()
        self.transport.chanel = sshchan

    # 1.接收从url中传过来的数据
    def dataReceived(self, data):
        Log(4, 'received data from url:[%s]' % data)
        if not hasattr(self.transport, "chanel"):
            # 后台和主机建立通道
            self.add_chanel(data)
        else:
            Log(4, 'self.transport has chanel....')
            self.exec_command(data)

    def connectionLost(self, reason):
        Log(3, "connect lost.....:{}, current threading:{}".format(reason, threading.active_count()))
        # self.sent('\r')
        # self.sent('connect lost.....')
        if hasattr(self.transport, "chanel"):
            self.transport.chanel.close()
        return

    def sent(self, message, encoding="cp1252"):
        try:
            message = normalize(message, encoding)
            json_msg = 'a{0}'.format(json.dumps([message], separators=(',', ':')))
            Log(4, "json_msg:{}".format(json_msg))
            if getattr(self.transport, "writeRaw", None) is not None:
                self.transport.writeRaw(json_msg)
            else:
                self.transport.write(message)
        except Exception as e:
            Log(1, "terminal sent error:{}".format(e.message))
            PrintStack()
