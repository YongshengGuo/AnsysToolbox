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
