#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20230611

import os

import socket

# def check_port(port, host='127.0.0.1'):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         s.connect((host, int(port)))
#         s.settimeout(1)
#         s.shutdown(2)
#         return True
#     except:
#         return False


# for i in range(100):
#     port = 8000+i
#     print("check port: %s"%port)
#     if check_port(port):
#         print("open help on: http://localhost:%s/"%port)
#         break

path = r"..\..\help\AnsysToolbox\site"
port = 8000
print("python -m http.server %s --directory %s"%(port,path))
os.system("python -m http.server %s --directory %s"%(port,path))
os.system("cmd \c http://localhost:%s/"%port)