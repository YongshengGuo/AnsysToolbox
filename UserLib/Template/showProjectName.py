#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20240220

import sys
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import MessageBox
print("This is a test progrom.")

Module = sys.modules['__main__']
if hasattr(Module, "oDesktop"):
    oDesktop = getattr(Module, "oDesktop")
else:
    raise Exception("oDesktop intial error.")


def main():
    
    oProject = oDesktop.GetActiveProject()
    oDesign = oProject.GetActiveDesign()
    msg = "Test information:\n"
    msg += "Version: %s\n"%oDesktop.GetVersion()
    msg += "InstallDir: %s\n"%oDesktop.GetExeDir()
    msg += "ProcessID: %s\n"%oDesktop.GetProcessID()
    if oProject:
        msg += "ProjectName: %s\n"%oProject.GetName()
    #     msg += "ProjectDir: %s\n"%oProject.GetPath()
    if oDesign:
        msg += "DesignName: %s\n"%oDesign.GetName()
        msg += "DesignType: %s\n"%oDesign.GetDesignType()
    print(msg)
    MessageBox.Show(msg)


# release()
if __name__ == '__main__':
#     test1()
    main()