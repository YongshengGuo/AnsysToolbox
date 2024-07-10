#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2023-04-09



import os,sys,re
import shutil
import time

from ..desktop import initializeDesktop,releaseDesktop

#---library
from ..definition.material import Materials

from ..common.complexDict import ComplexDict
from ..common.arrayStruct import ArrayStruct


from .object3DModel import Objects3DModle

# from .lib.common.common import *
from ..common.common import log,isIronpython #log is a globle variable
from ..common.unit import Unit



class HFSS(object):
    '''
    classdocs
    '''
    maps = {
        "InstallPath":"InstallDir",
        "Path":"ProjectPath",
        "Ver":"Version",
        }
    
    def __init__(self, version=None, installDir=None,usePyAedt=False):
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
            "UsePyAedt":usePyAedt,
            "PyAedtApp":None,
            "pyAedt":None,

            },maps=self.maps)
        
        self._info.update("Version", version)
        self._info.update("InstallDir", installDir)
        self._info.update("Log", log)
        self._info.update("Maps", self.maps)
        
        if not isIronpython and self._info["UsePyAedt"] == None:
            log.info("In cpython environment, UsePyAedt will set to True default. You could set it to False manually.")
            self._info.update("UsePyAedt", True)
        
        #----- 3D Layout object
        self._oDesktop = None
        self._oProject = None
        self._oDesign = None
        self._oEditor = None
        

        
        
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
            log.exception("layout should be intial use 'hfss.initDesign(projectName = None,designName = None)'")
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
        if key in ["_oDesktop","_oProject","_oDesign","_oEditor","_info"]:
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
        
    @property
    def oDesktop(self):
        if self.UsePyAedt and self._oDesktop == None: #use pyaedt lib
            if not self.PyAedt:
                log.debug("Try to load pyaedt.")
                try:
                    log.info("will initial oDesktop using PyLayout Lib... ")
                    self.pyAedt = __import__("pyaedt")
                    from pyaedt import launch_desktop
                    from pyaedt.desktop import release_desktop
                    self.PyAedtApp = launch_desktop(specified_version = self.version,new_desktop_session = False)
                    # app = Desktop(specified_version, non_graphical, new_desktop_session, close_on_exit, student_version, machine, port, aedt_process_id)
                except:
                    log.error("pyaedt lib must be installed, install command: pip install pyaedt")
                    log.error("if you don't want use pyaedt to intial pylayout, please set layout.usePyAedt = False before get oDesktop")
                    log.exception("pyaedt app intial error.")

            self._oDesktop == self.PyAedtApp.odesktop
            sys.modules["__main__"].oDesktop = self._oDesktop
        
        if self._oDesktop == None: 
            self._oDesktop = initializeDesktop(self.version,self.installDir)
            self.installDir = self._oDesktop.GetExeDir()
            sys.modules["__main__"].oDesktop = self._oDesktop
            
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
        #layout properties initial
        #----- 3D Layout object
#         self._oDesktop = None
        self._oProject = None
        self._oDesign = None
        self._oEditor = None
        oDesktop = self.oDesktop
        
#         log.debug("AEDT:"+self.Version)
        projectList = oDesktop.GetProjects()
        #for COM Compatibility, yongsheng guo #20240422
        if "ComObject" in str(type(projectList)):
            projectList = [projectList[i] for i in range(projectList.count)]
            
        if len(projectList)<1:
#             log.error("Must have one project opened in aedt.")
#             exit()
#             log.error("Must have one project opened in aedt.")
            log.warning("not found opened projects, insert new one.")
            oProject = oDesktop.NewProject()
            oProject.InsertDesign("HFSS", "HFSSDesign1", "", "")
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
                
        if not self._oProject:
            log.error("Must have one project opened in aedt.")
            raise Exception("Must have one project opened in aedt.")
        
        self._info.update("oProject",self._oProject)
        
        designList = self._oProject.GetTopDesignList()
        if len(designList)<1:
#             log.error("Must have one design opened in project.")
#             raise Exception("Must have one design opened in project.")
            self._oProject.InsertDesign("HFSS", "HFSSDesign1", "", "")
            self._oDesign = self._oProject.SetActiveDesign(designName)
        else:
        
            if designName:
                if designName not in designList:
                    log.error("design not in project.%s"%designName)
                    raise Exception("design not in project.%s"%designName)
                self._oDesign = self._oProject.SetActiveDesign(designName)
            else:
                self._oDesign = self._oProject.GetActiveDesign()
                if not self._oDesign:
                    log.info("try to get the first design")
                    self._oDesign = self._oProject.SetActiveDesign(designList[0])
                    
        #make sure the design is 3DL
        designtype = self._oDesign.GetDesignType()
        if designtype != 'HFSS':
            log.error("design type error, not HFSS design.")

        self._info.update("oDesign",self._oDesign)
        self._info.update("oEditor",self._oDesign.SetActiveEditor("3D Modeler"))
            
        self._info.update("ProjectName", self._oProject.GetName())
        self._info.update("DesignName", self.getDesignName(self._oDesign))
        self._info.update("projectDir", self._oProject.GetPath())
        
        self._info.update("ProjectPath", os.path.join(self._info.projectDir,self._info.projectName+".aedt"))
        self._info.update("EdbPath", os.path.join(self._info.projectDir,self._info.projectName+".aedb"))
        self._info.update("ResultsPath", os.path.join(self._info.projectDir,self._info.projectName+".aedtresults"))
        
        #Veraion C:\Program Files\AnsysEM\v231\Win64
        if self.version==None and self.installDir:
            splits = re.split(r"[\\/]+",self.installDir)
            ver1 = splits[-2] if splits[-1].strip() else splits[-3]
            ver2 = ver1.replace(".","")[-3:]
            self.version = "20%s.%s"%(ver2[0:2],ver2[2])
        
        
        #intial log, don't change log path, log will record in 3DL design
#         path = os.path.join(self._info.projectDir,"%s_%s.log"%(self._info.projectName,self._info.designName))
#         log.setPath(path)
#         log.info("Simulation log recorded in: %s"%path)
        
        log.info("init design: %s : %s"%(self.projectName,self.designName))
        
        #intial layout elements
        if initObjects:
            self.initObjects()

    def initObjects(self):
        
        info = self._info
        
        
        childNames = ["AllParts","CoordinateSystems","Groups","Lists","ModelParts","NonModelParts","Planes","Points","SubmodelDefinitions"]
        for name in childNames:
#             info.update(name,self.oEditor.GetChildNames(name))
            self.maps.update({
                name:{
                "Key":"DesignName",
                "Get": lambda v:self.oEditor.GetChildNames(name)
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

        info.update("Objects",Objects3DModle(app = self))
        info.update("Materials", Materials(layout = self))
 
    
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
            log.info("Add net Gruop: %s ------------ %s/%s"%(net,i,n))
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
                "Units:="        , "mil",
                "Rescale:="        , False,
                "Max Model Extent:="    , 10000
            ])
    
    def getUnit(self):
        return self.oEditor.GetModelUnits()
    #---functions

    
    #--- IO
    
    def newDesign(self,newDesignName,newPorjectName = None):
        if newPorjectName:
            oProject = self.oDesktop.NewProject()
            oProject.Rename(os.path.join(oProject.GetPath(),newPorjectName), True)
            oProject.InsertDesign("HFSS", newDesignName, "", "")
            self.initDesign(newPorjectName, newDesignName)
        else:
            self.oProject.InsertDesign("HFSS", newDesignName, "", "")
            self.initDesign(self.projectName, newDesignName)
    
    def openAedt(self,path):
        log.info("OpenProject : %s"%path)
        self.oDesktop.OpenProject(path)
        self.initDesign()
    
    def openArchive(self,archive,newPath):
        log.info("RestoreProjectArchive: %s"%archive)
        self.oDesktop.RestoreProjectArchive(archive, newPath, False, True) 
        self.initDesign()
    
    def reload(self):
        aedtPath = os.path.join(self.oProject.GetPath(),self.oProject.GetName()+".aedt")
        log.info("reload AEDT %s"%aedtPath)
        self.oProject.Save()
        self.oProject.Close()
        self.oDesktop.OpenProject(aedtPath)
        self.initDesign()


    def saveAs(self,path,OverWrite=True):
        log.info("save As %s"%path)
        self.oProject.SaveAs(path, OverWrite)
        self.initDesign()

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
    layout = HFSS("2023.2")
    layout.initDesign()
    layout.via1062
    layout.port[0]
    U8 = layout["Component:U8"]
    U9 = layout["Component:U8"]
    a= layout.Copper
    a["Resistivity"]= 1.0e-08
    layout.Layers.addLayer("L0")
    pins = U8.Pins
    layout.Port1
    pin = layout["U8_1"]
    dir(U8)
    pin = layout["Pin:U8-1"]
#     top = layout["Layer:C:0"]
    fr4= layout.Materials["FR4_epoxy"]
#     rst = layout.Solutions.getAllSetupSolution()
#     layout.Variables.test
    layout.release()
#     rst[0].exportSNP("c:\work\1.txt")
    pass