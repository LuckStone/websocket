#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz

import paramiko
import sys
import os
import socket
import select
import getpass
import termios
import tty
from paramiko.py3compat import u

tran = paramiko.Transport(('192.168.4.193', 22,))
tran.start_client()
tran.auth_password('root', '7ujm8ik,')

# ��һ��ͨ��
chan = tran.open_session()
# ��ȡһ���ն�
chan.get_pty()
# ������
chan.invoke_shell()


# ��ȡԭtty����
oldtty = termios.tcgetattr(sys.stdin)
try:
    # Ϊtty����������
    # Ĭ�ϵ�ǰtty�豸���ԣ�
    #   ����һ�лس���ִ��
    #   CTRL+C �����˳������������ַ������⴦��

    # ����Ϊԭʼģʽ������ʶ�����������
    # ���������ַ�Ӧ���ڵ�ǰ�նˣ�������ã������е��û���������͵�Զ�̷�����
    tty.setraw(sys.stdin.fileno())
    chan.settimeout(0.0)

    while True:
        # ���� �û����� �� Զ�̷������������ݣ�socket��
        # ������ֱ������ɶ�
        r, w, e = select.select([chan, sys.stdin], [], [], 1)
        if chan in r:
            try:
                x = u(chan.recv(1024))
                if len(x) == 0:
                    print('\r\n*** EOF\r\n')
                    break
                sys.stdout.write(x)
                sys.stdout.flush()
            except socket.timeout:
                pass
        if sys.stdin in r:
            x = sys.stdin.read(1)
            if len(x) == 0:
                break
            chan.send(x)

finally:
    # ���������ն�����,��������,�����ٴε�¼���޷�ʹ��
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


chan.close()
tran.close()