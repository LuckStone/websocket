# ָ�����ص�RSA˽Կ�ļ�,���������Կ��ʱ���õ������룬passwordΪ�趨�����룬���޲���ָ��password����
pkey = paramiko.RSAKey.from_private_key_file('/home/super/.ssh/id_rsa', password='12345')
# ��������
trans = paramiko.Transport(('192.168.2.129', 22))
trans.connect(username='super', pkey=pkey)

# ��sshclient�Ķ����transportָ��Ϊ���ϵ�trans
ssh = paramiko.SSHClient()
ssh._transport = trans

# ִ������ʹ�ͳ����һ��
stdin, stdout, stderr = ssh.exec_command('df -hl')
print(stdout.read().decode())

# �ر�����
trans.close()

#----------------------------------------------------------------------------------------------------

# ָ�����ص�RSA˽Կ�ļ�,���������Կ��ʱ���õ������룬passwordΪ�趨�����룬���޲���ָ��password����
pkey = paramiko.RSAKey.from_private_key_file('/home/super/.ssh/id_rsa', password='12345')
# ��������
ssh = paramiko.SSHClient()
ssh.connect(hostname='192.168.2.129',
            port=22,
            username='super',
            pkey=pkey)
# ִ������
stdin, stdout, stderr = ssh.exec_command('df -hl')
# ����ŵ�stdout�У�����д��󽫷ŵ�stderr��
print(stdout.read().decode())
# �ر�����
ssh.close()

#----------------------------------------------------------------------------------------------------

# ʵ����һ��transport����
trans = paramiko.Transport(('192.168.2.129', 22))
# ��������
trans.connect(username='super', password='super')

# ��sshclient�Ķ����transportָ��Ϊ���ϵ�trans
ssh = paramiko.SSHClient()
ssh._transport = trans
# ִ������ʹ�ͳ����һ��
stdin, stdout, stderr = ssh.exec_command('df -hl')
print(stdout.read().decode())

# �ر�����
trans.close()