# ʵ����һ��trans����# ʵ����һ��transport����
trans = paramiko.Transport(('192.168.2.129', 22))
# ��������
trans.connect(username='super', password='super')

# ʵ����һ�� sftp����,ָ�����ӵ�ͨ��
sftp = paramiko.SFTPClient.from_transport(trans)
# �����ļ�
sftp.put(localpath='/tmp/11.txt', remotepath='/tmp/22.txt')
# �����ļ�
# sftp.get(remotepath, localpath)
trans.close()