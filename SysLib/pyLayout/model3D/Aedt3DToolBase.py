#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2023-04-09



import os,sys,re
import shutil
import time

from ..desktop import initializeDesktop,releaseDesktop

#---library
from ..definition.padStack import PadStacks
from ..definition.componentLib import ComponentDefs
from ..definition.material import Materials
#---natural
from ..definition.setup import Setups
from ..definition.variable import Variables
from ..postData.solution import Solutions


from ..common.complexDict import ComplexDict
from ..common.arrayStruct import ArrayStruct

from .object3DModel import Objects3DModle

# from .lib.common.common import *
from ..common.common import log,isIronpython #log is a globle variable
from ..common.unit import Unit
from ..common.common import DisableAutoSave,ProcessTime

class Aedt3DToolBase(object):
    '''
    classdocs
    '''
    maps = {
        "InstallPath":"InstallDir",
        "Path":"ProjectPath",
        "Ver":"Version",
        }
    
    def __init__(self,toolType=None, version=None, installDir=None,nonGraphical=False,newDesktop=False):
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
        self._info.update("newDesktop", newDesktop)
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
#         self._oDesktop = None
#         self._info = None
#         self._components = None
#         self._setups = None
#         self._nets = None
#         self._layers = None
#         self._variables = None
#         self._ports = None
#         self._solutions = None
#         self._stackup = None
#         self._log = None
 
        releaseDesktop()
        
    def __getitem__(self, key):
        
        if not isinstance(key, str):
            log.exception("key for layout must be str: %s"%key)
        
        
        
        if key in self._info:
            return self._info[key]
        
        if not self._oDesign:
            log.exception("layout should be intial use '%s.initDesign(projectName = None,designName = None)'"%self._toolType)
            return
        
        log.debug("try to get element type: %s"%key)
        
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
    
    def __repr__(self):
        return "%s Object"%self.__class__.__name__
    
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
            self.PyAedtApp = launch_desktop(version = self.version,non_graphical=self.NonGraphical,new_desktop = self.newDesktop,close_on_exit=False)
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
        
        if self.NonGraphical:
            log.info("Will be intial oDesktop in nonGraphical mnode.")
        
        #try to intial by pyaedt
        if self.UsePyAedt:
            self.__initByPyaedt()

        #try to intial by internal method
        if self._oDesktop == None: 
            log.info("try to initial oDesktop using  internal method... ")
            self._oDesktop = initializeDesktop(self.version,self.installDir,nonGraphical=self.NonGraphical,newDesktop=self.newDesktop)
            self.installDir = self._oDesktop.GetExeDir()
            sys.modules["__main__"].oDesktop = self._oDesktop
            
        #intial error
        if self._oDesktop == None: 
            log.exception("Intial oDesktop error... ")
            
        return self._oDesktop
    
    
    def initProject(self,projectName = None):
        #layout properties initial
        #----- 3D Layout object
#         self._oDesktop = None
        self._oProject = None
#         self._oDesign = None
#         self._oEditor = None
        oDesktop = self.oDesktop
         
#         log.debug("AEDT:"+self.Version)
        projectList = oDesktop.GetProjectList()
        #for COM Compatibility, yongsheng guo #20240422
        if "ComObject" in str(type(projectList)):
            projectList = [projectList[i] for i in range(projectList.count)]
             
        if len(projectList)<1:
#             log.error("Must have one project opened in aedt.")
#             exit()
#             log.error("Must have one project opened in aedt.")
            log.warning("not found opened projects, insert new one.")
            oProject = oDesktop.NewProject()
            oProject.InsertDesign("HFSS 3D Layout Design", "Layout1", "", "")
            self._oProject = oProject
         
        else:
         
            if projectName:
    #             messageBox("projectName&designName")
                if projectName not in projectList:
                    log.error("project not in aedt.%s"%projectName)
                    raise Exception("project not in aedt.%s"%projectName)
                self._oProject = oDesktop.SetActiveProject(projectName)
     
            else:
                self._oProject = oDesktop.GetActiveProject()
                 
                if not self._oProject:
                    self._oProject = oDesktop.GetProjects()[0]
                    oDesktop.SetActiveProject(self._oProject.GetName())
                 
        if not self._oProject:
            log.error("Must have one project opened in aedt.")
            raise Exception("Must have one project opened in aedt.")
         
        self._info.update("oProject",self._oProject)

        self._info.update("ProjectName", self._oProject.GetName())
        self._info.update("projectDir", self._oProject.GetPath())
         
        self._info.update("ProjectPath", os.path.join(self._info.projectDir,self._info.projectName+".aedt"))
        self._info.update("ResultsPath", os.path.join(self._info.projectDir,self._info.projectName+".aedtresults"))
        self._info.update("EdbPath", os.path.join(self._info.projectDir,self._info.projectName+".aedb"))
 
        self._info.update("Version", self.oDesktop.GetVersion())
        self._info.update("InstallDir", self.oDesktop.GetExeDir())
        self._info.update("InstallPath", self.oDesktop.GetExeDir())
    
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
        #layout properties initial
        #----- 3D Layout object
#         self._oDesktop = None
        self._oProject = None
        self._oDesign = None
        self._oEditor = None
#         oDesktop = self.oDesktop
        
        self.initProject(projectName)

        #--- getDesignNames
        designList = self._oProject.GetTopDesignList()
        if len(designList)<1:
            log.error("Must have one design opened in project.")
            self._info.update("oDesign",None)
            self._info.update("oEditor",None)
            self._info.update("DesignName", "")

        else:
        
            if designName:
                if designName not in designList:
                    log.error("design not in project.%s"%designName)
                    raise Exception("design not in project.%s"%designName)
                self._oDesign = self._oProject.SetActiveDesign(designName)
            else:
                #update for 2025.1
                try:
                    self._oDesign = self._oProject.GetActiveDesign()
                except:
                    log.info("GetActiveDesign error.")
#                     log.info("try to get the first design")
#                     self._oDesign = self._oProject.SetActiveDesign(designList[0])
                
                #for 2024.2 GetActiveDesign() may return None
                if not self._oDesign:
                    log.info("try to get the first design")
                    self._oDesign = self._oProject.SetActiveDesign(designList[0])
                    
            
            #design type
            if self._toolType:
                designtype = self._toolType
            else:
                designtype = self._oDesign.GetDesignType()
            
            log.info("design type:%s"%designtype)  #exception if not 3DL design

            
            if designtype != self._toolType:
                log.error("deisgn: %s type %s not match with input type,  %s."% (self.getDesignName(self._oDesign),designtype, str(self._toolType)))
            
            self._info.update("oDesign",self._oDesign)
            self._info.update("DesignName", self.getDesignName(self._oDesign))
            
            if designtype == 'HFSS 3D Layout Design':
                self._info.update("oDesign",self._oDesign)
                self._info.update("oEditor",self._oDesign.SetActiveEditor("Layout"))
                self._info.update("DesignName", self.getDesignName(self._oDesign))
            else:
                self._info.update("oDesign",self._oDesign)
                self._info.update("oEditor",self._oDesign.SetActiveEditor("3D Modeler"))
                self._info.update("DesignName", self.getDesignName(self._oDesign))

            #initObjects
            if initObjects and designtype != 'HFSS 3D Layout Design':
                self.initObjects()


    def initObjects(self):
        
        info = self._info
        info.update("self",self)
        
        def _getObjects(self2,name):
            return self2.oEditor.GetChildNames(name)
        
        childNames = ["AllParts","CoordinateSystems","Groups","Lists","ModelParts","NonModelParts","Planes","Points","SubmodelDefinitions"]
        for name in childNames:
#             info.update(name,self.oEditor.GetChildNames(name))
            info.update(name,name)
            self.maps.update({
                name:{
                "Key":("self",name),
                "Get": lambda s,n:_getObjects(s,n)
                }})
            
#         oEditor.GetChildNames("AllParts")
#           self.oEditor.GetChildNames("Groups")
#         Name    Type    Description
#         <category>    String    
#         Optional. Passing no input returns the list of possible strings:
#         
#         "AllParts" – Returns the names of all parts.
#         "CoordinateSystems" – Returns the names of all coordinate systems.
#         "Groups" – Returns the names of all groups.
#         "Lists" – Returns the names of all lists.
#         "ModelParts" – Returns names of model parts.
#         "NonModelParts" – Returns the names of non-model parts.
#         "Planes" – Returns the names of all planes.
#         "Points" – Returns the names of all points.
#         "SubmodelDefinitions" – Returns the names of submodel definitions.


        info.update("Materials", Materials(layout = self))
        info.update("Variables", Variables(layout = self))
        info.update("Setups", Setups(layout = self))
        info.update("Solutions", Solutions(layout = self))
        info.update("PadStacks", PadStacks(layout = self))
        info.update("ComponentDefs", ComponentDefs(layout = self))
        
        info.update("Objects",Objects3DModle(app = self))
#         info.update("Primitives",Primitives(layout = self))
        info.update("unit",self.oEditor.GetModelUnits())
        info.update("Version",self.oDesktop.GetVersion())
        info.update("layout",self)
 
 
    
#     def getDesignName(self,oDesign):
#         return oDesign.GetName()
#     
#     def getDesignNames(self):
#         return [name for name in self._oProject.GetTopDesignList()]  
             
    def getDesignName(self,oDesign):
        return oDesign.GetName().split(';')[-1]
    
    def getDesignNames(self):
        return [name.split(';')[-1] for name in self._oProject.GetTopDesignList()]       
             
                
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
    
    @ProcessTime
    @DisableAutoSave
    def groupbyNets(self,netInfo):
        '''
        netInfo: {objName:net}
        '''
#         netInfo = ComplexDict(netInfo)
        netDict = {}
        for obj in self.Objects.NameList:
            if obj in netInfo:
                net = netInfo[obj]
                if net in netDict:
                    netDict[net].append(obj)
                else:
                    netDict[net] = [obj]
            else:
                log.debug("skip group object:%s"%obj)
        i = 1
        n = len(netDict)
        for net in netDict:
            #group name: Valid characters are letters, numbers, underscores
            group = re.sub(r"\W","_",net) #match [^a-zA-Z0-9]
            log.info(("Add net Gruop: %s"%net).ljust(50,"-") + "%s/%s"%(i,n))
            self.add2Group(group, netDict[net])
            i = i+1
    
    def add2Group(self,group,objs):
        if isinstance(objs, str):
            objs = [objs]
        else:
            objs = list(objs)
        
        if group in self.oEditor.GetChildNames("Groups"):
            log.debug("Add %s to group %s"%(",".join(objs),group))
            self.oEditor.MoveEntityToGroup(
                [
                    "Objects:="        , objs
                ], 
                [
                    "ParentGroup:="        , group
                ])
        else:
            self.createGroup(group, objs)

     
    def createGroup(self,group,objs=[]): 
        groupTemp = self.oEditor.GetChildNames("Groups")
        log.debug("Create group %s and add  %s"%(group,",".join(objs)))
        self.oEditor.CreateGroup(
            [
                "NAME:GroupParameter",
                "ParentGroupID:="    , "Model",
                "Parts:="        , ",".join(objs),
                "SubmodelInstances:="    , "",
                "Groups:="        , group #group name not work
            ])
        
        group2 = self.oEditor.GetChildNames("Groups")
        
        #get new group name
        newGroup = list(set(group2).difference(groupTemp))
        if newGroup:
            self.oEditor.SetPropertyValue("Attributes",newGroup[0],"Name",group)
            return newGroup[0]
        else:
            log.exception("Group create error: %s"%group)
        
        

    def setUnit(self, unit = "um"):
        #return old unit
        self.oEditor.SetModelUnits(
            [
                "NAME:Units Parameter",
                "Units:="        , unit,
                "Rescale:="        , False,
                "Max Model Extent:="    , 10000
            ])
    
    def getUnit(self):
        return self.oEditor.GetModelUnits()
    #---functions


    #--- IO
    
    def newProject(self,projectName):
        oProject = self.oDesktop.NewProject()
        oProject.Rename(projectName, True)
        return oProject
    
    
    def newDesign(self,newDesignName,projectName = None):
        if projectName:
            oProject = self.oDesktop.SetActiveProject(projectName)
            oProject.InsertDesign(self._toolType, newDesignName, "", "")
            self.initDesign(projectName, newDesignName)
        else:
            self.oProject.InsertDesign(self._toolType, newDesignName, "", "")
            self.initDesign(self.projectName, newDesignName)
            
        return self.oDesign
    
    def deleteProject(self):
        self.oDesktop.DeleteProject(self.ProjectName)
        self._oProject = None
        self._oDesign = None
        self._oEditor = None
    
    def deleteDesign(self):
        self.oProject.DeleteDesign(self.DesignName)
        self._oDesign = None
        self._oEditor = None

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

    
    @classmethod
    def quitAedt(cls):
        Module = sys.modules['__main__']
        if hasattr(Module, "oDesktop"):
            oDesktop = getattr(Module, "oDesktop")
            if oDesktop:
                oDesktop.QuitApplication()
    
    @classmethod
    def copyAEDT(cls,source,target):
        from shutil import copy
        #source = (source,source+".aedt")(".aedt" in source)
        if ".aedt" not in source:
            print("source must .aedt file: %s"%source)
            return
        if not os.path.exists(source):
            print("source file not found: %s"%source)
            return
        
        
        aedtTarget = (target+".aedt",target)[".aedt" in target]
        aedtTargetDir = os.path.dirname(aedtTarget)
        if not os.path.exists(aedtTargetDir):
            print("make dir: %s"%aedtTargetDir)
            os.mkdir(aedtTargetDir)
        
        copy(source,aedtTarget)
        
        edbSource = source[:-5]+".aedb" +"/edb.def"
        if os.path.exists(edbSource):
            edbTargetdir = aedtTarget[:-5]+".aedb"
            
            if not os.path.exists(edbTargetdir):
                print("make dir: %s"%edbTargetdir)
                os.mkdir(edbTargetdir)
            copy(edbSource,edbTargetdir)
        return aedtTarget


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


    @classmethod
    def isBatchMode(cls):
        Module = sys.modules['__main__']
        return hasattr(Module, "ScriptArgument")
    
    @classmethod
    def getScriptArgument(cls):
        Module = sys.modules['__main__']
        if hasattr(Module, "ScriptArgument"):
            return getattr(Module, "ScriptArgument")
        else:
            log.exception("Not running in batchmode")
    
    def getRelPath(self,path):
        
        try:
            relPath = os.path.relpath(path,self.ProjectDir)
            return os.path.join("$PROJECTDIR",relPath)
        except:
            return path


    def release(self):
        
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

#for test
if __name__ == '__main__':
#     layout = Layout("2022.2")
    layout = Aedt3DToolBase("2023.2")
    layout.initDesign()