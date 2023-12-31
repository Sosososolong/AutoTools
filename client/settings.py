"""
Settings for Client Tools project.

Generated by 'sosososolong'
"""

import os
import json


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Encoding
ENCODING = 'utf-8'

# Projects
PROJECTS = {
    # Configure a project
    # Choose a name and that name will display as an option in the console for selection
    'my project': {
        # An alias representing this project that may be used in other shell scripts for remote invocation
        # The alias can be passed into the command of remote invocation scripts in the form of a template '{{alias}}'.
        'appalias': 'mpn',
        # The directory where the deployment files are located. The supported operations for this directory include
        # uploading updates to a specific directory on the server, packaging it into a zip file and uploading it to a server directory, and executing remote commands
        # based on the UPLOAD configuration
        'path': 'D:/my.project.api/bin/Release/net5.0/publish/',
        # Only file paths containing 'my' and 'Dockerfile' will be uploaded
        'file_include_strs': 'my,Dockfile',
        # Files with paths containing 'appsettings.json' and 'wwwroot' will not be uploaded.
        'file_exclude_strs': 'appsettings.json,wwwroot'
    }
}


# Upload

UPLOAD = {
    'hosts': (
        # Parameter 1: Server IP;
        # Parameter 2: Port;
        # Parameter 3: Whether to upload a compressed package or a directory for the upload directory;
        # Parameter 4: The location on the server where the file is being uploaded.
        
        # Parameter 5: This is a remote execution script that runs a program, and after selecting the 'my project' project from the console
        #   {{name}} will be replaced with 'my project.zip', and {{alias}} will be replaced with 'mpn'.
        ('192.168.1.229', 9898, 'zip', '/var/wwwroot', 'mv -f /var/wwwroot/{{name}} /var/packages/'),
        ('192.168.1.229', 9898, 'dir', '/var/wwwroot', 'publish_images {{alias}}'),
    )
}


if os.path.exists(os.path.join(os.path.dirname(BASE_DIR), 'tools_settings.json')):
    settings_file = os.path.join(os.path.dirname(BASE_DIR), 'tools_settings.json')
    data = None
    with open(settings_file, 'r', encoding=ENCODING) as file:
        data = json.loads(file.read())
    if data:
        if 'projects' in data:
            PROJECTS = data["projects"]
        if 'upload' in data:
            UPLOAD = data['upload']


if __name__ == '__main__':
    # 作为配置文件, 它不是启动项目, 所以这里的代码不会运行, 可以在这里单独写一些测试程序
    str = '1,2,3,4'
    strArr = str.split(',')
    print(strArr)
    
