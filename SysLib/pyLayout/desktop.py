#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410


import os,sys,re
import shutil
import time

import clr
import os,sys,re
from .common.common import log

#---library
from .definition.padStack import PadStacks
from .definition.componentLib import ComponentDefs
from .definition.material import Materials
#---natural
from .definition.setup import Setups
from .definition.variable import Variables
from .postData.solution import Solutions

from .common.complexDict import ComplexDict
from .common.arrayStruct import ArrayStruct

from .layoutOptions import options

#log is a globle variable
from .common import common
from .common.common import *
# from .common.common import log,isIronpython
from .common.unit import Unit

from .common.common import DisableAutoSave,ProcessTime


'''初始化oDesktop对象

- 如果已经存在oDesktop对象，则直接返回oDesktop对象，比如已经初始化过oDesktop或者从AEDT启动脚本
- 当不存在oDesktop对象时，根据version 或者 installDir 返回oDesktop对象，同时打开AEDT窗口
- version和installDir都不指定时，会尝试启动最新版本的AEDT
- version和installDir都指定时， version优先级 高于 installDir

Examples:
    >>> oDesktop = initializeDesktop()
    打开最新版本AEDT,返回oDesktop对象
    >>> oDesktop = initializeDesktop(version = "Ansoft.ElectronicsDesktop.2013.1")
    打开版本 AEDT 2013R1

'''



# from .common.common import *

isIronpython = "IronPython" in sys.version

def initializeDesktop(version=None, installDir=None, nonGraphical = False):
    '''
    initializeDesktop'''
    #"2021.1"
    Module = sys.modules['__main__']
    if hasattr(Module, "oDesktop"):
        oDesktop = getattr(Module, "oDesktop")
        return oDesktop
    else:
        oDesktop = None
        
    #set installDir
    if oDesktop:
        aedtInstallDir = oDesktop.GetExeDir()
    elif installDir != None:
        aedtInstallDir = installDir.strip("/").strip("\\")
    else:
        #environ ANSYSEM_ROOTxxx, set installDir from version
        oDesktop = None
        if version == None:
            log.debug("version or installDir must set one")
            ANSYSEM_ROOTs = list(
                filter(lambda x: "ANSYSEM_ROOT" in x, os.environ))
            if ANSYSEM_ROOTs:
                log.debug("Try to initialize Desktop in latest version")
                ANSYSEM_ROOTs.sort(key=lambda x: x[-3:])
                verEnv = ANSYSEM_ROOTs[-1]
            else:
                log.debug("not found ANSYSEM_ROOT")
                return None
        else:
            #2022.1
            ver = version.replace(".", "")[-3:]
            verEnv = "ANSYSEM_ROOT%s" % ver
        if verEnv in os.environ:
            aedtInstallDir = os.environ[verEnv]
        else:
            raise ValueError("Do not found the install version %s" % version)
        
    sys.path.insert(0,aedtInstallDir)
    sys.path.insert(0,os.path.join(aedtInstallDir, 'PythonFiles', 'DesktopPlugin'))
    clr.AddReference("Ansys.Ansoft.DesktopPlugin")
    clr.AddReference("Ansys.Ansoft.CoreCOMScripting")
    clr.AddReference("Ansys.Ansoft.PluginCoreDotNet")
    
    if not oDesktop:
        # set version from aedtInstallDir
        if version == None:
            ver1 = re.split(r"[\\/]+", aedtInstallDir)[-2]
            ver2 = ver1.replace(".", "")[-3:]
            version = "Ansoft.ElectronicsDesktop.20%s.%s" % (ver2[0:2],ver2[2])
        else:
            pass
        
        try:
            log.info("Intial aedt desktop %s"%version)
            
#             #both for ironpython and python, not work
#             AnsoftCOMUtil = __import__("Ansys.Ansoft.CoreCOMScripting")
#             #COMUtil = AnsoftCOMUtil.Ansoft.CoreCOMScripting.Util.COMUtil
#             StandalonePyScriptWrapper = AnsoftCOMUtil.Ansoft.CoreCOMScripting.COM.StandalonePyScriptWrapper
#             if "Ansoft.ElectronicsDesktop" not in version:
#                 version = "Ansoft.ElectronicsDesktop." + version
#             log.debug(version)
#             if nonGraphical:
#                 oAnsoftApp = StandalonePyScriptWrapper.CreateObjectNew(nonGraphical)
#             else:
#                 oAnsoftApp = StandalonePyScriptWrapper.CreateObject(version)
#                  
#             oDesktop = oAnsoftApp.GetAppDesktop()

            if isIronpython:
                AnsoftCOMUtil = __import__("Ansys.Ansoft.CoreCOMScripting")
                #COMUtil = AnsoftCOMUtil.Ansoft.CoreCOMScripting.Util.COMUtil
                StandalonePyScriptWrapper = AnsoftCOMUtil.Ansoft.CoreCOMScripting.COM.StandalonePyScriptWrapper
                if "Ansoft.ElectronicsDesktop" not in version:
                    version = "Ansoft.ElectronicsDesktop." + version
                log.debug(version)
                if nonGraphical:
                    oAnsoftApp = StandalonePyScriptWrapper.CreateObjectNew(nonGraphical)
                else:
                    oAnsoftApp = StandalonePyScriptWrapper.CreateObject(version)
                      
                oDesktop = oAnsoftApp.GetAppDesktop()
            else:
                if nonGraphical:
                    #only for version last then 2024R1
                    import PyDesktopPlugin
                    oAnsoftApp = PyDesktopPlugin.CreateAedtApplication(NGmode=nonGraphical,alwaysNew = True)
                    oDesktop = oAnsoftApp.GetAppDesktop()
                else:
                    log.debug("Intial AEDT from python win32com")
                    import win32com.client  # @UnresolvedImport
                    oAnsoftApp = win32com.client.Dispatch(version)
                    oDesktop = oAnsoftApp.GetAppDesktop()
        except:
            log.debug("error initialize Desktop")
            oDesktop = None
    if oDesktop == None:
        raise ValueError("initialize Desktop fail")
    return oDesktop



def _delete_objects():
    module = sys.modules["__main__"]
    try:
        del module.COMUtil
    except AttributeError:
        pass

    try:
        del module.oDesktop
    except AttributeError:
        pass
    try:
        del module.pyaedt_initialized
    except AttributeError:
        pass
    try:
        del module.oAnsoftApplication
    except AttributeError:
        pass
    try:
        del module.desktop
    except AttributeError:
        pass
    try:
        del module.sDesktopinstallDirectory
    except AttributeError:
        pass
    try:
        del module.isoutsideDesktop
    except AttributeError:
        pass
    try:
        del module.AEDTVersion
    except AttributeError:
        pass
    try:
        del sys.modules["glob"]
    except:
        pass
    
    import gc
    gc.collect()


def releaseDesktop():
    '''
    releaseDesktop'''
#     release_desktop(close_projects=False, close_desktop=False)
    
    try:
        _delete_objects()
        return True
    except:
        return False



class AedtDesktopBase(object):
    '''
    classdocs
    '''
    maps = {
        "InstallPath":"InstallDir",
        "Path":"ProjectPath",
        "Ver":"Version",
        }
    
    def __init__(self,toolType="HFSS", version=None, installDir=None,nonGraphical=False):
        '''
        初始化PyLayout对象环境
        
        - version和installDir都为None，会尝试启动最新版本的AEDT
        - version和installDir都指定时， version优先级 高于 installDir
        Examples:
            >>> PyLayout()
            open least version AEDT, return PyLayout

            >>> PyLayout(version = "2013.1")
            open AEDT 2013R1, return PyLayout
        
        '''
        self._info = ComplexDict({
            "Version":None,
            "InstallDir":None,
            },maps=self.maps)
        
        self._info.update("Version", version)
        self._info.update("InstallDir", installDir)
        self._info.update("NonGraphical", nonGraphical)
        self._info.update("UsePyAedt", True)
        self._info.update("PyAedtApp", None)
        self._info.update("Log", log)
#         self._info.update("options",options)
        self._info.update("Maps", self.maps)
        
        if not isIronpython:
            log.info("In cpython environment, pyaedt shold be install, install command: pip install pyaedt")
#             self._info.update("UsePyAedt", True)
        
        #----- 3D Layout object
        self._oDesktop = None
        self._oProject = None
        self._oDesign = None
        self._oEditor = None
        self._toolType = toolType
        
    def __del__(self):
        if self.UsePyAedt and self.PyAedtApp:
            self.PyAedtApp.release_desktop()
        else:
            releaseDesktop()
        
    def __getitem__(self, key):
        
        if not isinstance(key, str):
            log.exception("key for layout must be str: %s"%key)
        
        if key in self._info:
            return self._info[key]
        
        if not self._oDesign:
            log.exception("layout should be intial use '%s.initDesign(projectName = None,designName = None)'"%self._toolType)
            return
        
        log.debug("try to get object: %s"%key)
        
        if key in self._info["Objects"]:
            return self._info["Objects"][key]
        
        log.exception("not found element on layout: %s"%key)
        return None
        
    def __setitem__(self, key,value):
        self._info[key] = value
        
        
    def __getattr__(self,key):
#         当调用一个不存在的属性时，就会触发__getattr__()
#         __getattribute__() 方法是无条件触发
        if key in ['__get__','__set__']:
            #just for debug run
            return None

        try:
            return super(self.__class__,self).__getattribute__(key)
        except:
            log.debug("Layout __getattribute__ from info: %s"%str(key))
            return self[key]
        
        
    def __setattr__(self, key, value):
        if key in ["_oDesktop","_oProject","_oDesign","_oEditor","_info","_toolType"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value
        
    def __dir__(self):
#         return object.__dir__(self)  + self.Props
        return dir(self.__class__) + list(self.__dict__.keys()) + self.Props
    
    @property
    def Info(self):
        return self._info
    
    @property
    def Props(self):
        propKeys = list(self.Info.Keys)
        if self.maps:
            propKeys += list(self.maps.keys())
             
        return propKeys
        
    def __initByPyaedt(self):    
        try:
            from pyaedt import launch_desktop
            log.info("try to initial oDesktop using PyLayout Lib... ")
            self.PyAedtApp = launch_desktop(version = self.version,non_graphical=self.NonGraphical,new_desktop = False)
            self.UsePyAedt = True
            self._oDesktop = self.PyAedtApp.odesktop
            sys.modules["__main__"].oDesktop = self._oDesktop
            log.logger = self.PyAedtApp.logger
#             self._info.update("Log", self.PyAedtApp._logger)
#             common.log = self.PyAedtApp._logger
        except:
            log.warning("pyaedt lib should be installed, install command: pip install pyaedt")
#             log.info("if you don't want use pyaedt to intial pylayout, please set layout.usePyAedt = False before get oDesktop")
            self.UsePyAedt = False
            log.warning("pyaedt app intial error.")
        
        
    @property
    def oDesktop(self):
        
        if self._oDesktop:
            return self._oDesktop
        
        #try to initial use pyaedt
        log.debug("Try to load pyaedt.")
        
        #try to get global oDesktop
        Module = sys.modules['__main__']
        if hasattr(Module, "oDesktop"):
            oDesktop = getattr(Module, "oDesktop")
            if oDesktop:
                self._oDesktop = oDesktop
                self.UsePyAedt = bool(self.PyAedtApp) #may be lanuched from aedt internal
                return oDesktop
        
        #try to intial by pyaedt
        if self.UsePyAedt:
            self.__initByPyaedt()

        #try to intial by internal method
        if self._oDesktop == None: 
            log.info("try to initial oDesktop using  internal method... ")
            self._oDesktop = initializeDesktop(self.version,self.installDir,nonGraphical=self.NonGraphical)
            self.installDir = self._oDesktop.GetExeDir()
            sys.modules["__main__"].oDesktop = self._oDesktop
            
        #intial error
        if self._oDesktop == None: 
            log.exception("Intial oDesktop error... ")
            
        return self._oDesktop
    
    
    def initDesign(self,projectName = None,designName = None, initObjects = True):
        '''Try to intial project properties.
        
        AEDT must have on project and design opened.
        
        - if projectName give, will be initialize the given project.
        - if designName give and the projectName must give, will be initialize the given project and design
        - if projectName and designName not give, it will try to initialize the firt project or design in AEDT
        
        Args:
            projectName (str): projectName to be actived, default is first project in aedt
            designName (str): designName to be actived, default is first design in project
        
        Exceptions:
            Not have project or design in AEDT
        
        '''
        log.exception("This method must be implemented by subclasses.")
 
        
        #intial layout elements
        if initObjects:
            self.initObjects()

    def initObjects(self):
        log.exception("This method must be implemented by subclasses.")
        

 
    
    def getDesignName(self,oDesign):
        return oDesign.GetName()
    
    def getDesignNames(self):
        return [name for name in self._oProject.GetTopDesignList()]  
                
    #--- design
        
    def enableAutosave(self,flag=True):
        Enabled = self.oDesktop.GetAutoSaveEnabled()
        
        if bool(flag) == Enabled:
            return Enabled
        
        if flag:
            self.oDesktop.EnableAutoSave(True)
        else:
            self.oDesktop.EnableAutoSave(False)
        
        return Enabled
  
        
    #--- IO
    
    def newDesign(self,newDesignName,newPorjectName = None):
        if newPorjectName:
            oProject = self.oDesktop.NewProject()
            oProject.Rename(os.path.join(oProject.GetPath(),newPorjectName), True)
            oProject.InsertDesign(self._toolType, newDesignName, "", "")
            self.initDesign(newPorjectName, newDesignName)
        else:
            self.oProject.InsertDesign(self._toolType, newDesignName, "", "")
            self.initDesign(self.projectName, newDesignName)
    
    def openAedt(self,path):
        log.info("OpenProject : %s"%path)
        self.oDesktop.OpenProject(path)
        self.initDesign(projectName=os.path.splitext(os.path.basename(path))[0])
    
    def openArchive(self,archive,newPath):
        log.info("RestoreProjectArchive: %s"%archive)
        self.oDesktop.RestoreProjectArchive(archive, newPath, False, True) 
        self.initDesign(projectName=os.path.splitext(os.path.basename(newPath))[0])
    
    def reload(self):
        aedtPath = os.path.join(self.oProject.GetPath(),self.oProject.GetName()+".aedt")
        log.info("reload AEDT %s"%aedtPath)
        self.oProject.Save()
        self.oProject.Close()
        self.oDesktop.OpenProject(aedtPath)
        self.initDesign(projectName=os.path.splitext(os.path.basename(aedtPath))[0])


    def saveAs(self,path,OverWrite=True):
        log.info("save As %s"%path)
        self.oProject.SaveAs(path, OverWrite)
        self.initDesign(projectName=os.path.splitext(os.path.basename(path))[0])

    def save(self):
        log.info("Save project: %s"%self.ProjectPath)
        self.oProject.Save()

    def close(self,save=True):
        if save:
            self.save()
        log.info("Close project: %s"%self.ProjectPath)
        self.oProject.Close()
            
    def deleteFromDisk(self):
        log.info("delete project from disk: %s"%self.ProjectPath)
        self.oDesktop.DeleteProject(self.projectName)
        if os.path.exists(self.resultsPath):
            log.info("delete project from disk: %s"%self.resultsPath)
            shutil.rmtree(self.resultsPath)

    #---message and job   
    def submitJob(self,host="localhost",cores=20):
        installPath = self.oDesktop.GetExeDir()
        jobId = "RSM_{:.5f}".format(time.time()).replace(".","")
        cmd = '"{exePath}" -jobid {jobId} -distributed -machinelist list={host}:-1:{cores}:90%:1 -auto -monitor \
                -useelectronicsppe=1 -ng -batchoptions "" -batchsolve {aedtPath}'.format(
                    exePath = os.path.join(installPath,"ansysedt.exe"),
                    jobId = jobId,
                    host = host, cores = cores, aedtPath = self.ProjectPath
                    )
        log.info("Project will be closed to submit job.")
        log.info("submit job ID: %s"%jobId)
        self.close(save=True)
        log.info(cmd)
        os.system(cmd)
        return jobId


    def release(self):
        
        if self.UsePyAedt and self.PyAedtApp:
            self.PyAedtApp.release_desktop()
        else:
            releaseDesktop()
            try:
                self._oEditor = None
                self._oDesign = None
                self._oProject = None
                self._oDesktop = None
                import gc
                gc.collect()
            except AttributeError:
                pass
