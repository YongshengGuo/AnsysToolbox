#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20240405



import sys,os
sys.path.append(r"C:\work\Study\Script\repository\win32API\AedtToolbox\magicBall\magicBall\bin\Release\SysLib")

Module = sys.modules['__main__']
if hasattr(Module, "oDesktop"):
    oDesktop = getattr(Module, "oDesktop")
else:
    raise Exception("oDesktop intial error.")


def closeAndSave():
    oProject = oDesktop.GetActiveProject()
    oProject.Save()
    print("Close project with Save: %s......"%oProject.GetName())
    oProject.Close() 
    
def closeNotSave():
    oProject = oDesktop.GetActiveProject()
    # oProject.Save()
    print("Close project  without Save: %s......"%oProject.GetName())
    oProject.Close() #Unsaved changes will be lost.

def closeAllProjectWithSave():
    projects = oDesktop.GetProjects()
    for oProject in projects:
        print("Close project with Save: %s......."%oProject.GetName())
        oProject.Save()
        oProject.Close()
        
def closeAllProjectWithoutSave():
    projects = oDesktop.GetProjects()
    for oProject in projects:
        # oProject.Save()
        print("Close project without Save: %s......"%oProject.GetName())
        oProject.Close() #Unsaved changes will be lost.

def ForceQuitAedt():
    oDesktop.QuitApplication()

def Reload():
    oProject = oDesktop.GetActiveProject()
    aedtPath = os.path.join(oProject.GetPath(),oProject.GetName()+".aedt")
    oProject.Close()
    print("Reload aedt:%s"%aedtPath)
    oDesktop.OpenProject(aedtPath)


# release()
if __name__ == "__main__":
    main()
