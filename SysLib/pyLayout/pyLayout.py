#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2023-04-09
'''
PyLayout对象代表AEDT中的一个Design对象，即一块PCB的对象，可以通过PyLayout对象对PCB上的器件，网络，图形，求解设定，结果数据进行访问。

相比AEDT的底层API,PyLayout提供了更加快捷和符合逻辑的访问方式。
```
PyLayout
|- Layers
|- Components
   |-pins
|- Nets
|- Variables
|- Lines
|- Vias
|- plane
|- log
```
所有的属性支持字典索引

- for Component, the key is refdes, support regular to match mutiple components
```
PyLayout.Components["U1"]  #获取U1器件的component对象
PyLayout.Components["U.*"]  #返回匹配以U开头器件的List
```
- for Nets, the key is netName, support regular to match mutiple nets
```
PyLayout.Nets["DDR3_A1"]  #获取DDR3_A1的Net对象
PyLayout.Nets["DDR3_A.*"]  #返回匹配DDR3_A.*的Net对象List
```
Examples：
    >>> PyLayout["Comp:U1"]  #获取U1器件的component对象
    >>> PyLayout["Net:A0"]  #获取U1器件的component对象
    >>> PyLayout["Pin:U1.A2"]  #获取U1器件的component对象
    >>> PyLayout["LC:0"]  #获取U1器件的component对象

'''

import os,sys,re
import shutil
import time

from .desktop import initializeDesktop,releaseDesktop

#---Primitive
from .primitive.component import Components
from .primitive.pin import Pins
from .primitive.port import Ports
from .primitive.line import Lines
from .primitive.via import Vias

#---library
from .definition.padStack import PadStacks
from .definition.componentLib import ComponentDefs
from .definition.material import Materials
#---natural
from .definition.layer import Layers
from .definition.setup import Setups
from .definition.net import Nets
from .definition.variable import Variables
from .postData.solution import Solutions

from .common.complexDict import ComplexDict
from .common.arrayStruct import ArrayStruct

from .layoutOptions import options

from .primitive.primitive import Primitives,Objects3DL
from .primitive.geometry import Polygen,Point

#log is a globle variable
from .common import common
from .common.common import *
# from .common.common import log,isIronpython
from .common.unit import Unit

class Layout(object):
    '''
    classdocs
    '''
    maps = {
        "InstallPath":"InstallDir",
        "Path":"ProjectPath",
        "Name":"DesignName",
        "Ver":"Version",
        "Comps":"Components"
        }
    
    #FindObjects 
    primitiveTypes = ['pin', 'via', 'rect','circle', 'arc', 'line', 'poly','plg', 'circle void','line void', 'rect void', 
           'poly void', 'plg void', 'text', 'cell','Measurement', 'Port', 'component', 'CS', 'S3D', 'ViaGroup']
    definitionTypes = ["Layer","Material","Setup","PadStack","ComponentDef","Variable","Net"]
    

    def __init__(self, version=None, installDir=None,nonGraphical=False):
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
        self._info.update("options",options)
        self._info.update("Maps", self.maps)
        
        if not isIronpython:
            log.info("In cpython environment, pyaedt shold be install, install command: pip install pyaedt")
#             self._info.update("UsePyAedt", True)
        
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
            log.exception("layout should be intial use method: 'Layout.initDesign(projectName = None,designName = None)'")
            return
        
        log.debug("try to get element type: %s"%key)
        
        for ele in self.primitiveTypes:
            collection = ele+"s"
            if key in self._info[collection]:
                log.debug("Try to return %s for key: %s"%(collection,key))
                return self._info[collection][key]
            
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
    
    
    def initDesign(self,projectName = None,designName = None, initLayout = True):
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
                
        if not self._oProject:
            log.error("Must have one project opened in aedt.")
            raise Exception("Must have one project opened in aedt.")
        
        self._info.update("oProject",self._oProject)
        
        designList = self.getDesignNames()
        if len(designList)<1:
#             log.error("Must have one design opened in project.")
#             raise Exception("Must have one design opened in project.")
            self._oProject.InsertDesign("HFSS 3D Layout Design", "Layout1", "", "")
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
        if designtype != 'HFSS 3D Layout Design':
            log.error("design type error, not 3D layout design.")

        self._info.update("oDesign",self._oDesign)
        self._info.update("oEditor",self._oDesign.SetActiveEditor("Layout"))
            
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
        
        
        #intial log
        path = os.path.join(self._info.projectDir,"%s_%s.log"%(self._info.projectName,self._info.designName))
        if self.UsePyAedt:
            import logging
            fileHandler = log.logger.logger.handlers[0]
            fileHandler2 = logging.FileHandler(path)
            fileHandler.stream = fileHandler2.stream
            fileHandler.baseFilename = path
            log.logger.logger.removeHandler(fileHandler)
            log.logger.logger.addHandler(fileHandler)
            del fileHandler2
            del fileHandler
            
        else:
            log.setPath(path)
            log.info("Simulation log recorded in: %s"%path)
        
        log.info("init design: %s : %s"%(self.projectName,self.designName))
        
        #intial layout elements
        self.enableICMode(False)
        
        if initLayout:
            self.initLayout()

    def initLayout(self):
        
        info = self._info
        
        #for Primitives
        classDict = ComplexDict(dict([(name.lower(),obj) for name,obj in globals().items() if isinstance(obj,type)]))
        
        for obj in self.primitiveTypes:
            key = obj.lower()+"s"
            if key.replace(" ","") in classDict:
                info.update(key,classDict[key](layout = self))
            else:
                info.update(key,Primitives(layout = self,type=obj))
            
            if " " in key:
                self.maps.update({key.replace(" ",""):key})

        #for collections
        info.update("Objects", Objects3DL(layout = self,types=".*"))
        info.update("Traces", Objects3DL(layout = self,types=['arc', 'line']))
        info.update("Shapes", Objects3DL(layout = self,types=[ 'rect','poly','plg']))
        info.update("Voids", Objects3DL(layout = self,types=['circle void', 'line void', 'rect void', 'poly void', 'plg void']))
        
        
        info.update("Layers", Layers(layout = self))
        info.update("Materials", Materials(layout = self))
        info.update("Variables", Variables(layout = self))
        info.update("Setups", Setups(layout = self))
        info.update("Nets", Nets(layout = self))
        info.update("Solutions", Solutions(layout = self))
        info.update("PadStacks", PadStacks(layout = self))
        info.update("ComponentDefs", ComponentDefs(layout = self))
        
#         info.update("Primitives",Primitives(layout = self))
        info.update("unit",self.oEditor.GetActiveUnits())
        info.update("Version",self.oDesktop.GetVersion())
        
        #intial geometry definition
        Polygen.layout = self
        Point.layout = self
        
    def getDesignName(self,oDesign):
        return oDesign.GetName().split(';')[-1]
    
    def getDesignNames(self):
        return [name.split(';')[-1] for name in self._oProject.GetTopDesignList()]  
                
    #--- design
        
    def clip(self,newDesignName, includeNetList, clipNetList, expansion = "2mm",InPlace=False):

        cutList = []
        for net in includeNetList:
            cutList.append("net:=")
            cutList.append([net,False])

        for net in clipNetList:
            cutList.append("net:=")
            cutList.append([net,True])
        
        #delete nets that not used
        kNets = includeNetList + clipNetList
        delNet = list(filter(lambda n:n not in kNets,self.Nets.NetNames))
        log.debug("delete nets not used in cutout: %s"%",".join(delNet))
        self.Nets.deleteNets(delNet)
        
        log.info("Cut out layout by net: %s"%",".join(kNets))
        log.info("Cutout expansion: %s"%expansion)
        self.oEditor.CutOutSubDesign(
            [
                "NAME:Params",
                "Name:="        , newDesignName,
                "InPlace:="        , InPlace,
                "AutoGenExtent:="    , True,
                "Type:="        , "Conformal",
                "Expansion:="        , expansion,
                "RoundCorners:="    , True,
                "Increments:="        , 1,
                "UseSelection:="    , False,
                "ExtentSel:="        , [],
                [
                    "NAME:Nets",
#                     "net:="            , ["M_MA_4_",False],
#                     "net:="            , ["GND",True]
                ] + cutList
            ])
        
    def _merge(self,layout2,solderOnComponents = None,align = None,solderBallSize = "14mil,14mil", stackupReversed = False, prefix = ""):
        '''
            合并另外一个layout对象，叠层在Z轴叠加
        connect = [(pin1,pin2),(pin_1,pin_2)] #用于对齐
        solderOnComponents = {U1:(14mil,14mil),U2:None} #确定哪些位置长solderball
        次方法为完全实现，建议不要使用。
        '''
        log.info("Merge layers from {layout2} to {layout1}".format(layout1=self.designName,layout2=layout2.designName))
        layers2 = layout2.Layers
#         solderHeight = "14mil"
#         solderDiameter  = "14mil"
        solderHeight,solderDiameter = solderBallSize.split(",",1)
        
        #add solder ball
        self.Layers.S1.addLayerAbove(name = prefix + "SolderBall",typ = "dielectric", copy = None)
        self.Layers.S1.Material = "air"
        self.Layers.S1.Thickness = solderHeight
        
        #layers from layout2
        layers2 = layers2[::-1] if stackupReversed else layers2
        copyLayersDsp = []
        for layer2 in layers2:
            copyLayersDsp.append("%s:%s"%(layer2.Name,prefix + layer2.Name))
        #add solderball layers
        copyLayersDsp.append("0:%s"%(prefix + "SolderBall"))
        #add self layers
        for layer in self.Layers:
            copyLayersDsp.append("0:%s"%(layer.Name))
            
        
        #add from bottom layer
        for layer2 in layers2[::-1]:
            name2 = prefix + layer2.Name
            self.Layers.S1.addLayerAbove(name = name2, copy = layer2)
        
        #copy objs
        allObjs = layout2.oEditor.FindObjects('Type','*')
        layout2.oEditor.Copy(allObjs)
        self.oEditor.Paste(
            [
                "NAME:offset",
                "xy:="            , [0,0]
            ], 
            [
                "NAME:merge",
                "StackupLayers:="    , copyLayersDsp,
                "DrawLayers:="        , ["SIwave Regions:SIwave Regions","Measures:Measures","Outline:Outline","Rats:Rats","Errors:Errors","Symbols:Symbols","Postprocessing:Postprocessing"]
            ])
        log.info("Finished copy {0} object to {1}".format(len(allObjs),self.designName))

    def autoHFSSRegions(self):
        self.oEditor.GenerateSuggestedHFSSRegions()

    def enableICMode(self,flag=True):
        try:
            if flag:
                self.oDesign.DesignOptions(
                    [
                        "NAME:options",
                        "ModeOption:="        , "IC mode"
                    ], 0)
            else:
                self.oDesign.DesignOptions(
                    [
                        "NAME:options",
                        "ModeOption:="        , "General mode"
                    ], 0)
        except:
            log.error("enableICMode error: %s"%str(flag))

    def enableAutosave(self,flag=True):
        Enabled = self.oDesktop.GetAutoSaveEnabled()
        
        if bool(flag) == Enabled:
            return Enabled
        
        if flag:
            self.oDesktop.EnableAutoSave(True)
        else:
            self.oDesktop.EnableAutoSave(False)
        
        return Enabled

    #--- objects
    
    def getObjects(self,type="*"):
        '''
        "Type" to search by object type.
        Valid <value> strings for this type include: 'pin', 'via', 'rect', 'arc', 'line', 'poly', 'plg', 'circle void', 
        'line void', 'rect void', 'poly void', 'plg void', 'text', 'cell', 'Measurement', 'Port', 'Port Instance', 
        'Port Instance Port', 'Edge Port', 'component', 'CS', 'S3D', 'ViaGroup'
        '''
        if type.lower() == "all":
            type = "*"
            
        return self.layout.oEditor.FindObjects('Type',type)
    
    def getObjectsbyNet(self,net,type="*"):
        
        if type.lower() == "all":
            type = "*"
            
        return self.oEditor.FilterObjectList('Type', type, self.oEditor.FindObjects('Net',net))
        
    def getObjectsbyLayer(self,layer,type="*"):
        
        if type.lower() == "all":
            type = "*"
        return self.oEditor.FilterObjectList('Type', type, self.oEditor.FindObjects('Layer',layer))
    
    def getObjectsBySquare(self,center,layer="*",sideLength="1mil"):
        '''
        suggest to use getObjectByPoint
        '''
        return self.getObjectByPoint(center, layer, sideLength)
         
        
    def getObjectByPoint(self,point,layer="*",radius=0):
        
        if len(point)!=2:
            log.exception("center must be list with length 2")
            
        X,Y = [Unit(p).V for p in point]
        
        if radius == 0:
            posObj = self.oEditor.FindObjectsByPoint(self.oEditor.Point().Set(X, Y), layer)
            return list(posObj)
        
        else:
            l = Unit(radius).V
            p0 = self.oEditor.Point().Set(X-l/2, Y-l/2)
            p1 = self.oEditor.Point().Set(X+l/2, Y-l/2)
            p2 = self.oEditor.Point().Set(X+l/2, Y+l/2)
            p3 = self.oEditor.Point().Set(X-l/2, Y+l/2)
            box = self.oEditor.Polygon().AddPoint(p0).AddPoint(p1).AddPoint(p2).AddPoint(p3).SetClosed(True)
            posObj = self.oEditor.FindObjectsByPolygon(box, layer)
            return list(posObj)
        
    def setUnit(self, unit = "um"):
        #return old unit
        return self.oEditor.SetActiveUnits(unit)
    
    def getUnit(self):
        return self.oEditor.GetActiveUnits()
    
    def delete(self,objs):
        '''
        objs: names of delete objs
        '''
        if isinstance(objs, str):
            objs = [objs]
            
        for name in objs:
            try:
                obj = self.Objects[name]
                self[obj.Type+"s"].pop(name)
            except:
                log.warning("%s: delete error from layout."%name)
                
        self.oEditor.Delete(objs)
        self.Objects.refresh()
        self.Traces.refresh()
        self.Shapes.refresh()
        self.Voids.refresh()

        

    
    #---functions

    
    #--- IO
    
    def newDesign(self,newDesignName,newPorjectName = None):
        if newPorjectName:
            oProject = oDesktop.NewProject()
            oProject.Rename(os.path.join(oProject.GetPath(),newPorjectName), True)
            oProject.InsertDesign("HFSS 3D Layout Design", newDesignName, "", "")
            self.initDesign(newPorjectName, newDesignName)
        else:
            self.oProject.InsertDesign("HFSS 3D Layout Design", newDesignName, "", "")
            self.initDesign(self.projectName, newDesignName)
    
    def translateLayout(self,layoutPath,edbOutPath = None, controlFile = "", extractExePath = None, layoutType = None):
        
        if extractExePath:
            if extractExePath[-4:].lower() == ".exe":
                extractExePath = os.path.dirname(extractExePath)
                
            if extractExePath not in os.environ['PATH']:
                split = ";" if 'nt' in os.name else ":"
                os.environ['PATH'] = split.join([extractExePath,os.environ['PATH']])
                log.debug(os.environ['PATH'])
                
        installPath = self.oDesktop.GetExeDir()
        if installPath not in os.environ['PATH']:
            split = ";" if 'nt' in os.name else ":"
            os.environ['PATH'] = split.join([installPath,os.environ['PATH']])
            log.debug(os.environ['PATH'])
        
        if not edbOutPath:
            edbOutPath = layoutPath[:-4] + ".aedb"
        if not controlFile:
            cmd = "anstranslator {input} {output}".format(input=layoutPath,output=edbOutPath)
        else:
            cmd = "anstranslator {input} {output} -c={controlFileName}".format(input=layoutPath,output=edbOutPath,controlFileName=controlFile)
        os.system(cmd)
        
        return edbOutPath
    
    def loadLayout(self,layoutPath ,edbOutPath = None,controlFile = "", layoutType = None):
        '''
        doc
        '''
   
        if not layoutType:
            if layoutPath[-4:].lower() in [".brd",".mcm",".sip"]:
                layoutType = "Cadence"
            elif layoutPath[-4:].lower() in [".siw"]:
                layoutType = "SIwave"
            elif layoutPath[-5:].lower() in [".aedt","aedtz"]:
                layoutType = "AEDT"
            elif layoutPath[-5:].lower() in [".aedb"]:
                layoutType = "EDB"
            elif layoutPath[-7:].lower() in ["edb.def"]:
                layoutType = "EDB"
                
            elif layoutPath[-4:].lower() in [".tgz"]:
                layoutType = "ODB++"
                
            elif layoutPath[-4:].lower() in [".gds"]:
                layoutType = "GDS"
                
            else:
                raise Exception("Layout type must be specified")
        
        if layoutType.lower() == "aedt":
            self.layout.openAedt(layoutPath)
        elif layoutType.lower() == "edb":
            self.layout.importEBD(layoutPath)
        elif layoutType.lower() == "cadence":
            if not edbOutPath:
                edbOutPath = layoutPath[:-4] + ".aedb"
            if not controlFile:
                controlFile = ""
            self.importBrd(layoutPath,edbOutPath,controlFile)
        else:
            raise Exception("Unknow layout type")
    
    def importEBD(self,path):
        if path[-4:] == "aedb":
            path = os.path.join(path,"edb.def")
            
        aedtPath = os.path.dirname(path)[-5:] + ".aedt"
        if os.path.exists(aedtPath):
            self.openAedt(aedtPath)
            return
        
        if not os.path.exists(path):
            log.exception("EDB file not exist: %s"%path)
            
        log.info("load edb : %s"%path)
        oTool = self.oDesktop.GetTool("ImportExport")
        oTool.ImportEDB(path)
        self.initDesign()
        
    def importBrd(self,path,edbPath = None, controlFile = ""):
        '''
        Imports a Cadence Extracta file into a new project.
        '''
        
        if edbPath == None:
            edbPath = path[-3:]+"aedb"
            
        oTool = self.oDesktop.GetTool("ImportExport")
        oTool.ImportExtracta(path, edbPath, controlFile)
        self.initDesign()
        
    def openAedt(self,path):
        log.info("OpenProject : %s"%path)
        self.oDesktop.OpenProject(path)
        self.initDesign()
    
    def openArchive(self,archive,newPath):
        log.info("RestoreProjectArchive: %s"%archive)
        self.oDesktop.RestoreProjectArchive(archive, newPath, False, True) 
        self.initDesign()
    
    def reload(self):
        aedtPath = self.ProjectPath
        log.info("reload AEDT %s"%aedtPath)
        self.oProject.Save()
        self.oProject.Close()
        self.oDesktop.OpenProject(aedtPath)
        self.initDesign()


    def reloadEdb(self):
        
        aedtPath = os.path.join(self.oProject.GetPath(),self.oProject.GetName()+".aedt")
        edbPath = os.path.join(self.oProject.GetPath(),self.oProject.GetName()+".aedb")
        log.info("reload Edb %s"%edbPath)
        self.oProject.Save()
        self.oProject.Close()
        if os.path.exists(aedtPath):
            os.remove(aedtPath)
        self.importEBD(edbPath)
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
    
    @classmethod
    def copyAs(cls,source,target):
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
        edbTargetdir = aedtTarget[:-5]+".aedb"
        
        if not os.path.exists(edbTargetdir):
            print("make dir: %s"%edbTargetdir)
            os.mkdir(edbTargetdir)
        copy(edbSource,edbTargetdir)
        return aedtTarget

    #---analyze and job   
    def analyze(self):
        self.oDesign.AnalyzeAll()
    
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
    
    def setCores(self,croes,hpcType = None):
        '''
        cores (int): 
        hpcType (str): Pack or Workgroup
        '''
        
        oDesktop = self.oDesktop
        #worked
        activeHPCOption = oDesktop.GetRegistryString("Desktop/ActiveDSOConfigurations/HFSS 3D Layout Design")
        log.info("ActiveDSOConfigurations: %s"%activeHPCOption)
        #oDesktop.SetRegistryString(r"Desktop/DSOConfigurationsEx/HFSS 3D Layout Design/%s/NumCores"%activeHPCOption)
        activeHpcStr = oDesktop.GetRegistryString("Desktop/DSOConfigurationsEx/HFSS 3D Layout Design/%s"%activeHPCOption)
        
        cores_old = re.findall(r"NumCores=(\d+)", activeHpcStr)
        
        if cores_old and int(cores_old[0])!=int(croes):
            activeHpcStr = re.sub(r"NumCores=\d+","NumCores=%s"%int(croes), activeHpcStr)
            
            
    #         #not work
    #         log.info('set Active HPC Configuration "%s":  NumCores=%s'%(activeHPCOption,croes))
    #         oDesktop.SetRegistryString("Desktop/DSOConfigurationsEx/HFSS 3D Layout Design/%s"%activeHPCOption,activeHpcStr)
    #         
            #workaround
            scfStr = "$begin 'Configs'\n$begin 'Configs'\n%s$end 'Configs'\n$end 'Configs'\n"%activeHpcStr
            pathScf = os.path.join(self.projectDir,"hpc.acf")
            writeData(scfStr, pathScf)
            log.info('set Active HPC Configuration "%s":  NumCores=%s'%(activeHPCOption,croes))
            self.oDesktop.SetRegistryFromFile(pathScf)
        else:
            log.info("ActiveDSOConfigurations have the same cores as required")
        
        if hpcType:
            self.setHPCType(hpcType)

        
    def setHPCType(self,hpcType):
        '''
        hpcType (str): Pack or Workgroup
        '''
        if hpcType:
            #oDesktop.GetRegistryString("Desktop/Settings/ProjectOptions/HPCLicenseType")
            log.info('set HPCLicenseType: %s'%(hpcType))
            self.oDesktop.SetRegistryString("Desktop/Settings/ProjectOptions/HPCLicenseType",hpcType)
        
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
    
    #---message  

    def message(self,msg,level = 0):
        global oDesktop
        log.debug(msg)
        self.oDesktop.AddMessage("","",0,msg)


    def release(self):
        
        releaseDesktop()
        try:
            self._info = None
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
    layout = Layout("2023.2")
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