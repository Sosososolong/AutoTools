from datetime import datetime
import multiprocessing
import os
from socket import AF_INET, SOCK_STREAM, socket
from time import time

BUFFER_SIZE = 8192# 1024 * 1024
def get_path_separator(target_path) -> str:
    if target_path.find('/') >= 0:
        return '/'
    else:
        return '\\'

# TODO: include_strs => searchPatterns
def find_files(search_path, include_strs=None, exclude_strs=None) -> list:
    """
    查找指定目录下所有的文件(不包含以__开头和结尾的文件)或指定格式的文件
    :param search_path: 查找的目录路径
    :param include_strs: 获取文件名包含指定字符串的文件
    :param exclude_strs: 过滤掉文件名包含某些字符串的文件
    """
    if include_strs is None:
        include_strs = []
    if exclude_strs is None:
        exclude_strs = []

    files = []
    # 获取路径下所有文件
    names = os.listdir(search_path)
    for name in names:
        path = os.path.abspath(os.path.join(search_path, name))
        if os.path.isfile(path):
            include_any = False
            # 如果不包含指定字符串
            if len(include_strs) == 0:
                include_any = True
            else:
                for include_str in include_strs:
                    if include_str in name:
                        include_any = True
                        break
                if not include_any:
                    continue

            # 没有break, 说明不包含exclude_strs中的字符
            is_ok = True
            for filter_str in exclude_strs:
                if filter_str in name:
                    is_ok = False
                    break
            if not is_ok:
                continue

            files.append(path.replace('\\', '/'))
        else:
            files += find_files(path, include_strs=include_strs, exclude_strs=exclude_strs)
    return files


def is_path(file_name):
    return os.path.isabs(file_name) or os.path.isabs(os.path.expanduser(file_name))


# 获取file同级目录下的file_anme的绝对路径
def get_abs_path(file_anme, file):
    if os.path.isabs(file_anme):
        return file_anme
    else:
        return os.path.join(os.path.dirname(file), file_anme).replace('\\', '/')


def copy_file(file, old_folder_anme, new_folder_name, q):
  """复制文件"""
  try:
    old_f = open(file, 'rb')
    content = old_f.read()
    old_f.close()

    old_folder_anme = old_folder_anme.rstrip('\\').rstrip('/')
    new_folder_name = new_folder_name.rstrip('\\').rstrip('/')
    # file:'E:\agent\a.txt' => E:\agent    \ a.txt => 获取文件相对路径a.txt
    file_path = file.replace(old_folder_anme, '')
    separator = file_path[0]
    file_relative_path = file_path.lstrip(separator)
    new_file = os.path.join(new_folder_name, file_relative_path)

    # new_file目录是否存在
    file_dir = os.path.dirname(new_file)
    if not os.path.exists(file_dir):
      try:
        # 并发时, 有可能有多个线程同时创建同一个多级目录, 此时当一个线程将该目录创建好了, 其他线程尝试创建的时候发现目录已存在就会抛异常:"当文件已存在时，无法创建该文件"
        os.makedirs(file_dir)
      except:
        pass

    new_f = open(new_file, 'wb')
    new_f.write(content)
    new_f.close()
  except Exception as ex:
    print(ex)

    # copy完文件后, 向队列中写入一个消息, 这样主进程就可以根据队列里面的消息知道copy进度了
  q.put(file)


def copy_dir():
  # 1. 获取要copy的文件夹的名字
  old_folder_name = input('请输入要copy的文件夹的路径:')
  # 2. 创建一个新的文件夹
  new_folder_name = old_folder_name + '[copyed]'
  if not os.path.exists(new_folder_name):
    os.mkdir(new_folder_name)
  # 3. 获取要copy 的文件夹 中所有的文件 listdir()
  files = find_files(old_folder_name)

  # 4. 创建进程池
  po = multiprocessing.Pool(5)

  # 5. 创建一个队列
  q = multiprocessing.Manager().Queue()
  
  start = time()
  
  # 6. 向进程池中添加copy文件的任务
  for file in files:
    # 同步方式(实测不到一秒, 进程池却要七八秒????)
    # copy_file(file, old_folder_name, new_folder_name, q)
    
    # 进程池
    po.apply_async(copy_file, args=(file, old_folder_name, new_folder_name, q))

  po.close()
  # po.join()

  all_file_num = len(files)  # 所有文件个数
  copyed_num = 0
  while True:
    file = q.get()
    copyed_num += 1
    # "\r" 表回到行首, end默认值是换行,这里不换行
    float_value = copyed_num * 100 / all_file_num
    int_value = int(copyed_num * 100 / all_file_num)
    print('\rcoping %s %.2f  %%' % (('=' * (int(int_value) - 1)) + '>', float_value), end='')
    if copyed_num >= all_file_num:
      break
  # 换行
  print()
  print(time() - start)


def show_processing_bar(current_value, all_value):
    per = all_value / 100
    # "\r" 表回到行首, end默认值是换行,这里不换行
    float_value = current_value / per
    int_value = int(float_value)
    end = '' if current_value < all_value else '\n'
    # 每次打印频率太高, 多发送一些数据打印一次
    #if current_value % (10240) == 0 or float_value == 100:
    print('\r\tprocessing %s %.2f  %%' % (('=' * (int(int_value) - 1)) + '>', float_value), end=end)


class Uploader(object):
    def __init__(self, host=None, port=None, encoding='utf-8', remote_save_dir=None, filename_include_str=None, filename_exclude_str=None) -> None:
        self.encoding = encoding
        self.host = host
        self.port = port
        self.remote_save_dir = remote_save_dir
        self.filename_include_str = filename_include_str
        self.filename_exclude_str = filename_exclude_str

        self.tcp_client = socket(AF_INET, SOCK_STREAM)
        # 2. **连接服务器**(区分于UDP, 明确这里是客户端, 去连接服务器)
        self.tcp_client.connect((host, port))
        # try:
        #     self.tcp_client.connect((host, port))
        # except:
        #     # 异常就要终端程序, 继续运行没有意义
        #     print('服务器连接失败')
        #     return


    def __del__(self):
        if self.tcp_client.recv(1024).decode(self.encoding) == 'ready':
            self.tcp_client.send('-1'.encode(self.encoding))
            if self.tcp_client.recv(1024).decode(self.encoding) == '-1':
                print('client closed')
                self.tcp_client.close()


    def upload(self, target):
        if not target or not os.path.exists(target):
            return

        print(f'uploading: {target}')

        if os.path.isdir(target):
            self.upload_dir(target)
        else:
            self.upload_file(target)


    def upload_dir(self, dir):
        if not os.path.isdir(dir):
            print(f'{dir}不是一个目录')
        # 获取目录中的所有文件(绝对路径)
        files = find_files(dir, include_strs=self.filename_include_str, exclude_strs=self.filename_exclude_str)
        for file in files:
            #if time() - os.path.getmtime(file) < 60:
            #print(file) # datetime.fromtimestamp(os.path.getmtime(file))
            
            dir = dir.replace('\\', '/')
            file = file.replace('\\', '/')
            file_relative_path = file.replace(dir, '').strip('/').strip('\\')
            self.upload_file(file, file_relative_path)

    def upload_file(self, file, file_relative_path=None):
        if not file:
            print(f'{file}不是文件')
            return

        # 参数协议: 表示即将发送文件(1)以及文件的相对路径(file_relative_path)
        if not file_relative_path:
            filesplit = os.path.split(file) # ('c:/temp/iduo.form', 'iduo.form.api.dll')
            file_relative_path = filesplit[1]
        
        # 等待服务端处理好一个文件再发送新的文件
        if self.tcp_client.recv(1024).decode(self.encoding) == 'ready_for_new':
            # 文件大小
            file_size = os.stat(file).st_size
            sended_bytes = 0

            # 1: 表示发送文件; 文件的相对路径; 文件在服务端的保存路径; 文件的大小
            self.tcp_client.send(f'1;;;;{file_size};;;;{file_relative_path};;;;{self.remote_save_dir}'.encode(self.encoding))
            
            print(f'file: {file}; server: {self.host}:{self.port}; file_relative_path: {file_relative_path}; host_save_dir: {self.remote_save_dir}')
            
            response = self.tcp_client.recv(1024).decode(self.encoding)
            if response == 'ready_for_file_content':
                buffer_size = BUFFER_SIZE

                with open(file, 'rb') as f:
                    while True:
                        content = f.read(buffer_size)
                        if not content:
                            # 退出while循环, 发送000000给服务端, 表示当前文件的数据已发送完毕, 提醒服务端准备好接收下一个文件信息
                            break
                        
                        content_length = self.tcp_client.send(content)
                        # print(f'\t发送文件: {len(content)} - {content_length} bytes(字节)')
                        sended_bytes += content_length
                        show_processing_bar(sended_bytes, file_size)

                    self.tcp_client.send('000000'.encode(self.encoding))

def main():
    # files = find_files('D:\\.NET\\iduo\\Doc\\download\\temp\\iduo.site.api', include_strs=['.dll']) # 只要dll文件
    #files = find_files('D:\\.NET\\iduo\\Doc\\download\\temp\\iduo.site.api', exclude_strs=['.dll']) # 除了dll文件
    #files = find_files('D:\\.NET\\iduo\\Doc\\download\\temp\\iduo.site.api', include_strs=['iduo', 'site']) # 只要包含iduo和site的文件
    files = find_files('D:\\.NET\\iduo\\iduo.form\\iduo.form.api\\bin\\Release\\net5.0\\publish')
    i = 0
    for f in files:
        i += 1
        print(f'{i}: {f}')
    
    #Uploader('192.168.1.81', 8989, 'utf-8', 'D:/.NET/iduo/Doc/download/temp').upload('D:/others.projects/tools/zips/iduo.site.api.zip')
    #Uploader('192.168.1.81', 8989, 'utf-8', 'D:/.NET/iduo/Doc/download/temp/iduo.site.api', '.dll').upload('D:/others.projects/tools/zips/publish')

if __name__ == '__main__':
    main()