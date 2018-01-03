# 实例化一个trans对象# 实例化一个transport对象
trans = paramiko.Transport(('192.168.2.129', 22))
# 建立连接
trans.connect(username='super', password='super')

# 实例化一个 sftp对象,指定连接的通道
sftp = paramiko.SFTPClient.from_transport(trans)
# 发送文件
sftp.put(localpath='/tmp/11.txt', remotepath='/tmp/22.txt')
# 下载文件
# sftp.get(remotepath, localpath)
trans.close()