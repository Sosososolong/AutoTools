from datetime import datetime
import os
from client.file_utils import Uploader, get_path_separator
from client.settings import PROJECTS, ENCODING, UPLOAD
from client.ssh_conn import SSHConnection


def main():
    # args = sys.argv
    # if len(args) == 1:
    #     return
    
    # target_dir = args[1]

    key_index_dic = {}
    key_index = 1
    for key in PROJECTS.keys():
        key_index_dic.setdefault(str(key_index), key)
        print(f'[{key_index}] {key}')
        key_index += 1
    selected_index = input('请选择要打包的项目:')
    
    # iduo.application.api
    app_name = key_index_dic[selected_index]
    
    # 要上传的目录D:/xxx/bin/Release/net5.0/publish/(上传方式可能是zip可能是dir)
    target_dir = PROJECTS[app_name]['path'].replace('\\', '/')

    appalias =  PROJECTS[app_name]['appalias']

    remote_app_dir_name = PROJECTS[app_name].get('remote_app_dir_name')
    # 文件需要包含的字符串
    file_include_strs = PROJECTS[app_name]['file_include_strs']
    file_include_strs = None if not file_include_strs else file_include_strs
    file_exclude_strs = PROJECTS[app_name]['file_exclude_strs']
    file_exclude_strs = None if not file_exclude_strs else file_exclude_strs
    
    print(f'target_dir: {target_dir}')
    separator = '/'
    
    # 上传至多个服务器
    for h in UPLOAD['hosts']:
        host = h[0]
        port = h[1]
        transfer_type = h[2]
        host_save_dir = h[3].replace('\\', '/')
        remote_cmds = None
        if len(h) == 5:
            remote_cmds = h[4]
        
        # 1. 上传文或者目录
        if transfer_type == 'dir':
            host_app_dir = app_name if remote_app_dir_name is None else remote_app_dir_name
            host_app_dir = host_app_dir if host_save_dir.endswith('/') else f'/{host_app_dir}'
            app_dir_abspath = f'{host_save_dir}{host_app_dir}' # /home/administrator/web/pro_dir
            
            file_include_strs_arr = file_include_strs.split(',') if file_include_strs else None
            file_exclude_strs_arr = file_exclude_strs.split(',') if file_exclude_strs else None
            Uploader(host, port, ENCODING, app_dir_abspath, file_include_strs_arr, file_exclude_strs_arr).upload(target_dir)
        elif transfer_type == 'zip':
            # 截取字符串: strname[start : end : step] 不包含end
            # dir_parts = target_dir[0:bin_index].split(separator)
            
            current_abspath = os.path.abspath('.')
            zips_dir = f'{current_abspath}{separator}zips{separator}'
            if not os.path.exists(zips_dir):
                os.mkdir(zips_dir)
            ziped_file = f'{zips_dir}{app_name}.zip'
            # if os.path.exists(ziped_file) and time() - os.path.getmtime(ziped_file) < 10:
            #     print(f'文件刚刚{datetime.fromtimestamp(os.path.getmtime(ziped_file))}已更新')
            #     return

            if not target_dir.endswith('/') and not target_dir.endswith('\\'):
                target_dir += separator

            cmd = f'7z a .{separator}zips{separator}{app_name}.zip "{target_dir}"'
            print(f'cmd: {cmd}')
            print('开始打包')
            # 正确执行完成返回-1, 失败返回1
            if os.system(cmd) == 1:
                print('打包失败')
                return
            
            # popen的方式需要读取出内容, 单纯的popen()方法不阻塞, cmd命令还没执行完就会执行其他下一行代码
            # with os.popen(cmd, 'r') as zip_log:
            #     zip_log_content = zip_log.read()
            #     print(zip_log_content)
            Uploader(host, port, ENCODING, host_save_dir).upload(ziped_file)
        else:
            print(f'{host}:{port} 为指定zip或者dir的方式上传')
        
        # ssh连接服务器执行命令
        if remote_cmds is not None:
            if appalias is not None:
                remote_cmds = remote_cmds.replace('{{alias}}', appalias)
                remote_cmds = remote_cmds.replace('{{name}}', f'{app_name}.zip')
            ssh = SSHConnection(host, 22, 'root', "C:/Users/Wu Qianlin/.ssh/id_rsa")
            
            print(f'execute: {remote_cmds}')
            stdout, stderr = ssh.exec(remote_cmds)
            print(f'{stdout}\n{stderr}')

    print('\n\n\n\n')

if __name__ == '__main__':
    main()
