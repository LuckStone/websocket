# -*- coding: utf-8 -*-
import paramiko
import sys
import os
import socket
import getpass

# from paramiko.py3compat import u

# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False

def interactive_shell(chan):
    if has_termios:
        posix_shell(chan)
    else:
        windows_shell(chan)


def posix_shell(chan):
    import select

    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)
        f = open('handle.log','a+')
        tab_flag = False
        temp_list = []
        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = chan.recv(1024)
                    if len(x) == 0:
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    if tab_flag:
                        if x.startswith('\r\n'):
                            pass
                        else:
                            f.write(x)
                            f.flush()
                        tab_flag = False
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                if x == '\t':
                    tab_flag = True
                else:
                    f.write(x)
                    f.flush()
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


def windows_shell(chan):
    import threading

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass


def run():
    # 获取当前登录用户
    """
    
        host_list = [
            {'host': "192.168.11.139", 'username': 'oldboy', 'pwd': "123"},
            {'host': "192.168.11.138", 'username': 'oldboy', 'pwd': "123"},
            {'host': "192.168.11.137", 'username': 'oldboy', 'pwd': "123"},
        ]
        for item in enumerate(host_list, 1):
            print(item['host'])
    
        num = raw_input('序号：')
        sel_host = host_list[int(num) -1]
        hostname = sel_host['host']
        username = sel_host['username']
        pwd = sel_host['pwd']
        print(hostname,username,pwd)
    """

    tran = paramiko.Transport((hostname, 22,))
    tran.start_client()
    tran.auth_password(username, pwd)
    # 打开一个通道
    chan = tran.open_session()
    # 获取一个终端
    chan.get_pty()
    # 激活器
    chan.invoke_shell()

    interactive_shell(chan)

    chan.close()
    tran.close()


if __name__ == '__main__':
    run()