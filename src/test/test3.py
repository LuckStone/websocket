# -*-coding=utf-8-*-

import paramiko
import os
import select
import sys
import tty
import termios

'''
ʵ��һ��xshell��¼ϵͳ��Ч������¼��ϵͳ�Ͳ�����������ͬʱ���ؽ��
֧���Զ���ȫ��ֱ�ӵ��÷������ն�

'''
# ����һ��socket
trans = paramiko.Transport(('192.168.2.129', 22))
# ����һ���ͻ���
trans.start_client()

# ���ʹ��rsa��Կ��¼�Ļ�
'''
default_key_file = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
prikey = paramiko.RSAKey.from_private_key_file(default_key_file)
trans.auth_publickey(username='super', key=prikey)
'''
# ���ʹ���û����������¼
trans.auth_password(username='super', password='super')
# ��һ��ͨ��
channel = trans.open_session()
# ��ȡ�ն�
channel.get_pty()
# �����նˣ������Ϳ��Ե�¼���ն��ˣ��ͺ�������������xshell��¼ϵͳһ��
channel.invoke_shell()

# ��ȡԭ�����ն�����
oldtty = termios.tcgetattr(sys.stdin)
try:
    # �����ڵĲ����ն���������Ϊ�������ϵ�ԭ���ն�����,����֧��tab��
    tty.setraw(sys.stdin)
    channel.settimeout(0)

    while True:
        readlist, writelist, errlist = select.select([channel, sys.stdin,], [], [])
        # ������û�����������,sys.stdin�����仯
        if sys.stdin in readlist:
            # ��ȡ��������ݣ�����һ���ַ�����1���ַ�
            input_cmd = sys.stdin.read(1)
            # ������͸�������
            channel.sendall(input_cmd)

        # �����������˽��,channelͨ�����ܵ����,�����仯 select��֪��
        if channel in readlist:
            # ��ȡ���
            result = channel.recv(1024)
            # �Ͽ����Ӻ��˳�
            if len(result) == 0:
                print("\r\n**** EOF **** \r\n")
                break
            # �������Ļ
            sys.stdout.write(result.decode())
            sys.stdout.flush()
finally:
    # ִ��������ڵ��ն����Իָ�Ϊԭ�����ն�����
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

# �ر�ͨ��
channel.close()
# �ر�����
trans.close()