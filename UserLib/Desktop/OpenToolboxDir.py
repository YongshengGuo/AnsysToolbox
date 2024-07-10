#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20240405



import sys,os
appPath = os.path.realpath(__file__)
appDir = os.path.split(appPath)[0] 

def main():
    toolDir = os.path.dirname(os.path.dirname(appDir))
    os.system("start " + toolDir)



# release()
