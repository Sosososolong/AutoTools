# pip install paramiko报错: C:\Program Files (x86)\Windows Kits\10\include\10.0.22000.0\ucrt\inttypes.h(61): error C2143: 语法错误: 缺少“{”, 原因是该文件14行代码"#include <stdint.h>"找不到stdint.h
# 解决办法: 将"D:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC\14.34.31933\include\stdint.h"复制到"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\ucrt"目录下; inttypes.h的第14行代码可以将尖括号改为双引号
import paramiko
from os import path

class SSHConnection(object):
    def __init__(self, host, port, user, pwd_or_pkey) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.pwd_or_pkey = pwd_or_pkey
        self.__client = None
        self.__sftp = None
        self.__sftp = None


    def __del__(self):
        if self.__client is not None:
            self.__client.close()
        if self.__sftp is not None:
            self.__sftp.close()
            self.__tran.close()
        
    
    def create_client(self):
        if self.__client is None:
            if path.isfile(self.pwd_or_pkey):
                # 配置私钥文件位置
                private = paramiko.RSAKey.from_private_key_file("C:/Users/Wu Qianlin/.ssh/id_rsa")
                self.__client = paramiko.SSHClient()
                self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.__client.connect(hostname=self.host, port=self.port, username=self.user, pkey=private)
            else:
                # 创建ssh客户端对象
                self.__client = paramiko.SSHClient()
                self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.__client.connect(self.host, self.port, self.user, self.pwd_or_pkey)
        return self.__client
    

    def create_sftp(self):
        if self.__sftp is None:
            # 创建一个通道, sftp会使用它
            self.__tran = paramiko.Transport((self.host, self.port))
            self.__tran.connect(username=self.user, password=self.pwd_or_pkey)

            # 创建sftp对象
            self.__sftp = paramiko.SFTPClient.from_transport(self.__tran)
        return self.__sftp
    

    def exec(self, cmd):
        self.create_client()
        stdin, stdout, stderr = self.__client.exec_command(cmd)
        return (stdout.read().decode('utf8'), stderr.read().decode('utf8'))

    
    def upload(self, localpath, remotepath):
        self.create_sftp()
        put_info = self.__sftp.put(localpath, remotepath, confirm=True)
    
    
    def download(self, localpath, remotepath):
        self.create_sftp()
        self.__sftp.get(remotepath=remotepath, localpath=localpath)
        print('下载完成')


    