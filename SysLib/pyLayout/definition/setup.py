#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2023-04-24

'''
setupName for hfss 3D Layout

Examples:
    Add HFSS setupName and Sweep
    >>> setup1 = Setup.add("setup1")
    >>> setup1.addSweep("sweepName")
    
    >>> setup1["setup1"]
    return Setup object of "setup1"
'''

import re,os
from ..common import hfss3DLParameters
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common.unit import Unit
from ..common.common import log,tuple2list


class Sweep(object):
    
    '''
    hfss3DLParameters.hfssSweep
    '''
    
    mapsForHFSS = {
        "SweepData":"Sweeps/Data",
        "UseQ3D":"UseQ3DForDC",
        "Tolerance":"SAbsError",
        "InterpolatingTolerance":"SAbsError",
        "SweepType":{"Key":"FreqSweepType",
                     "Get": lambda x: x[1:],
                     "Set":lambda x: {"interpolating":"kInterpolating","discrete":"kDiscrete"}[x.lower()]} #kInterpolating or discrete
        
        }
    
    mapsForSIwave = {
        "SweepData":"Sweeps/Data",
        "UseQ3D":"UseQ3DForDC",
        "Tolerance":"RelativeSError",
        "InterpolatingTolerance":"RelativeSError",
        "SweepType":{"Key":"FreqSweepType",
                     "Get": lambda x: x[1:],
                     "Set":lambda x: {"interpolating":"kInterpolating","discrete":"kDiscrete"}[x.lower()]} #kInterpolating or discrete
        }
    
    
    layoutTemp = None
    def __init__(self,sweepName = None,setupName=None,layout=None):
        self.name = sweepName
        self.setupName = setupName
        
        if setupName == None:
            #sweepName must be full Name,like: SweepName:SetupName
            setup_sweep = sweepName.split(",")
            if len(setup_sweep) != 2:
                log.exception("if setupName not give,sweepName must be FullName as: 'setupName:Sweep'.")
            
            self.setupName,self.name = setup_sweep
        
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
        else:
            self.layout = self.__class__.layoutTemp
        
        self._oModule = None
        self._array = None
        self.maps = {}

    def __getitem__(self, key):
        return self.Info[key]
    
    def __setitem__(self, key,value):
        self.Info[key] = value
        self.oModule.EditSweep(self.setupName,self.name,self.Info.Array)
#         self.oModule.Edit(self.name,self.Info.Array)
        self._array = None
        
    def __getattr__(self,key):

        if key in ["layout","name","setupName","_array","_oModule","maps"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]

         
    def __setattr__(self, key, value):
        if key in ["layout","name","setupName","_array","_oModule","maps"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value
        
    def __repr__(self):
        return "Sweep Object: %s"%self.Name

    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)
    
    @property
    def Props(self):
        propKeys = list(self.Info.Keys)
        
        if self.maps:
            propKeys += list(self.maps.keys())
             
        return propKeys


    @property
    def Name(self):
        return self.name
    
    @property
    def FullName(self):
        return "%s:%s"%(self.setupName,self.name)
    
    @property
    def oModule(self):
        if not self._oModule:
            self._oModule = self.layout.oDesign.GetModule("SolveSetups")
        return self._oModule
    
    @property
    def Info(self):
        if self._array == None:
            self.parse()
        return self._array
    
    
    def parse(self):
        SolveSetupType =  self.layout.Setups[self.setupName].SolveSetupType 
        
        self.maps = {}
        if SolveSetupType== "HFSS":
            self.maps = self.mapsForHFSS
        elif SolveSetupType== "SIwave":
            self.maps = self.mapsForSIwave
        else:
            log.error("Unknow setup type:%s"%self.setupName)
 
        self._array = ArrayStruct(tuple2list(self.oModule.GetSweepInfo(self.setupName,self.name)),maps=self.maps)
#         self._array = ArrayStruct(self.oModule.GetSweepInfo(self.setupName,self.name),maps=self.maps)

    def delete(self):
        self.oModule.DeleteSweep(self.setupName,self.name)
    
#     def getData(self,path = None):
#         datas = ArrayStruct(self.oModule.GetSweepInfo(self.setupName,self.name))
#         if not path:
#             return datas
#         
#         return datas.get(path)
#     
#     def setData(self,path=None,value=None,arrayDatas = None):
#         if arrayDatas:
#             self.oModule.EditSweep(self.setupName,self.name,arrayDatas)
#             return
#         datas = ArrayStruct(self.oModule.GetSweepInfo(self.setupName,self.name))
#         datas.set(path,value)
#         self.oModule.EditSweep(self.setupName,self.name,datas.Array)
    
    def analyze(self):
        self.oModule.AnalyzeSweep(self.setupName,self.name)
    
    @classmethod
    def getByName(cls,SetupName,sweepName):
        sweepNames = Setup.getByName(SetupName).getSweepNames()
        
        for name in sweepNames:
            if sweepName.lower() == name.lower():
                return cls(sweepName)
            
        raise Exception("Sweep '%s' not in setupName '%s'"%(sweepName,SetupName))

    @classmethod
    def getByFullName(cls,fullName):
        '''
        Full Name: setupName:Sweep
        '''
        
        setup_sweep = fullName.split(",")
        if len(setup_sweep) != 2:
            raise Exception("FullName must give by 'setupName:Sweep'.")
        
        return cls.getByName(*setup_sweep)

class Setup(object):
    layoutTemp = None
    maps = {
        "AdaptiveFrequency":"AdaptiveSettings/SingleFrequencyDataList/AdaptiveFrequencyData/AdaptiveFrequency",
        "DeltaS": "AdaptiveSettings/SingleFrequencyDataList/AdaptiveFrequencyData/MaxDelta",
        "Order": {"Key":"AdvancedSettings/OrderBasis",
                  "Set":lambda x:[-1,1,2][("mixed","first","second").index(x.lower())],
                  "Get":lambda y:("mixed","first","second")[(-1,1,2).index(y)],
                  },
        "MaxPasses": "AdaptiveSettings/SingleFrequencyDataList/AdaptiveFrequencyData/MaxPasses"
        }
    
    def __init__(self,name = None,layout=None):
        
        self.name = name
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
            Sweep.layoutTemp = layout
        else:
            self.layout = self.__class__.layoutTemp
            
        self._oModule = None
        self._array = None
    
    def __getitem__(self, key):
        
        if key.lower() == "sweeps":
            sweepNames = self.oModule.GetSweeps(self.name)
            if len(sweepNames):
                return ComplexDict(dict([(sweepName,Sweep(sweepName,self.name,layout=self.layout)) for sweepName in sweepNames]))
            else:
                log.info("Not sweeps in setup: %s"%self.name)
                return []
        
        return self.Info[key]
    
    def __setitem__(self, key,value):
        self.Info[key] = value
        self.oModule.Edit(self.name,self.Info.Array)
        self._array = None
        
    def __getattr__(self,key):

        if key in ["layout","name","_array","_oModule"]:
            object.__getattribute__(self,key)
        else:
            log.debug("Layer __getattribute__ from _info: %s"%str(key))
            return self[key]

         
    def __setattr__(self, key, value):
        if key in ["layout","name","_array","_oModule"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value
        
    def __repr__(self):
        return "Setup Object: %s"%self.Name
    
    
    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)
    
    @property
    def Props(self):
        propKeys = list(self.Info.Keys)
        propKeys.append("sweeps")
        if self.maps:
            propKeys += list(self.maps.keys())
             
        return propKeys
    
    @property
    def oProject(self):
        return self.layout.oProject
    
    @property
    def oDesign(self):
        return self.layout.oDesign

    @property
    def oEditor(self):
        return self.layout.oEditor

    @property
    def oModule(self):
        if not self._oModule:
            self._oModule = self.oDesign.GetModule("SolveSetups")
        return self._oModule
    
    @property
    def Info(self):
        if self._array == None:
            self.parse()
        return self._array
    
    @property
    def Name(self):
        return self.name
    
    #--- setupName
    
#     def getData(self,path=None):
#         datas = self.Info #ArrayStruct(self.oModule.GetSetupData(self.name),maps=self.maps)
#         if not path:
#             return datas
#         return datas.get(path)
#     
#     def setData(self,path=None,value=None,arrayDatas = None):
#         if arrayDatas: #arrayDatas has High priority
#             self.oModule.Edit(self.name,arrayDatas)
#             self._array = None
#             return None
#         
#         datas = self.Info # ArrayStruct(self.oModule.GetSetupData(self.name))
#         datas.set(path,value)
#         self.oModule.Edit(self.name,datas.Array)
#         #update Info
#         self._array = None
    
    def delSetup(self):
        self.oModule
    
    def parse(self):
        self._array = ArrayStruct(tuple2list(self.oModule.GetSetupData(self.name)),maps=self.maps)
        
    
    #--- Sweep
    def findSweep(self,sweepName):
        for swp in self.getSweepNames():
            if swp.lower() == sweepName:
                log.info("Sweep exist: %s."%swp)
                return swp
            
        return False
    
    def addSweep(self,sweepName):
        swp = self.findSweep(sweepName)
        if swp:
            log.info("Sweep already exist: %s %s"%(self.name,sweepName))
            return Sweep(swp,self.name)

        log.info("Sweep already exist: %s %s"%(self.name,sweepName))
#         self.oModule.AddSweep(self.name,["NAME:%s"%sweepName])
        
        self.oModule.AddSweep(self.name, 
            [
                "NAME:%s"%sweepName,
                [
                    "NAME:Properties",
                    "Enable:="        , "true"
                ],
                [
                    "NAME:Sweeps",
                    "Variable:="        , sweepName,
                    "Data:="        , "LIN 0GHz 10GHz 0.01GHz",
                    "OffsetF1:="        , False,
                    "Synchronize:="        , 0
                ]
            ])
        
        
        return Sweep(sweepName,self.name)
        
    
    def delSweep(self,sweepName):
        swp = self.findSweep(sweepName)
        if swp:
            self.oModule.DeleteSweep(self.name,swp)
    
    def getSweep(self,sweepName):
        for swp in self.getSweepNames():
            if swp.lower() == sweepName:
                return Sweep(swp,self.name)
        
        log.exception("Sweep not found: %s"%sweepName)
    
    def getAllSweeps(self):
        return [Sweep(self.name,sweepName) for sweepName in self.oModule.GetSweeps(self.name)]
    
    def getSweepNames(self):
        return self.oModule.GetSweeps(self.name)
    
    def getSweepData(self,sweepName,path = None):
        datas = ArrayStruct(self.oModule.GetSweepInfo(self.name,sweepName))
        if not path:
            return datas
        
        return datas.get(path)
    
    def setSweepData(self,sweepName,path=None,value=None,arrayDatas = None):
        if arrayDatas:
            self.oModule.EditSweep(self.name,sweepName,arrayDatas)
            return
        datas = ArrayStruct(self.oModule.GetSweepInfo(self.name,sweepName))
        datas.set(path,value)
        self.oModule.EditSweep(self.name,sweepName,datas.Array)
        
    #--- Analyze 
    
    def analyze(self):
        self.oDesign.Analyze(self.name)
    
    def exportToHfss(self,path = None,timeout = 10*60):
        if not path:
            path = os.path.join(self.layout.projectDir, "%s_%s.aedt"%(self.layout.projectName,self.layout.designName))
            
        log.info("Export 3D Layout design to HFSS: %s"%path)
        self.oModule.ExportToHfss(self.name, path)
        
        #wait for output
        import time
        i = 0
        timeout = 20*60
        while(i<timeout):
            if os.path.exists(path):
                break
            time.sleep(2) #sleep 1s
            i += 2
            
            if i%5 == 0:
                log.info("Wait for hfss project ready: %ss"%i)
            
        if i>=timeout:
            log.exception("export to hfss failed.")
            
        
#         for net in self.layout.Nets:
#             for obj in net.getConnectedObjs():
#                 netInfo.update({obj:net.name})
        
        from ..model3D.HFSS import HFSS
        hfss = HFSS()
        hfss.openAedt(path)
        unit = hfss.getUnit()
        netInfo = {}
        for obj in hfss.Objects:
            #skip sheet objects
            if "Material" not in obj:
                log.debug("%s not have Material property, skip."%obj.name)
                continue
            
            #skip dielectric
            if not hfss.Materials[obj.Material].isConductor():
                log.debug("%s is dielectric object, skip."%obj.name)
                continue
            
            pt0 = ["%s%s"%(x,unit) for x in  obj.Vertexs[0]]
            layer = self.layout.layers.getLayerByHeight(pt0[2])
            layoutObjs = self.layout.getObjectByPoint([pt0[0],pt0[1]],layer=layer)
            if layoutObjs:
                net = None
                for obj2 in layoutObjs:
                    if "Net" in  self.layout[obj2].Props:
                        net = self.layout[obj2].Net
                        break
                    else:
                        continue
                if not net:
                    log.error("obj %s not found."%obj2.name)
                else:
                    netInfo.update({obj.name:net})
            else:
                log.debug("Not found object on layout:%s"%obj.name)                 
        
        hfss.groupbyNets(netInfo)
                
        return path
    
    
    #--- mesh
#         
#     def addMeshOperationOnNets(self,nets,meshLength = '5mil'):
#         oDesign = self.oDesign
#         log.debug("add mesh opertion on nets: meshlength %s"%meshLength)
#         layers = self.getSignalLayers()
#         meshOperations = [
#             [
#                 "NAME:MeshEntityInfo",
#                 "IsFcSel:="        , False,
#                 "EntID:="        , -1,
#                 "FcIDs:="        , [],
#                 [
#                     "NAME:MeshBody",
#                     "Id:="            , -1,
#                     "Nam:="            , "",
#                     "Mat:="            , "",
#                     "Layer:="        , layer,
#                     "Net:="            , net,
#                     "OrigNet:="        , net
#                 ],
#                 "BBox:="        , []
#             ] for net in nets for layer in layers
#         ]
#         
#         oModule = oDesign.GetModule("SolveSetups")    
#         setupName = self.getSetups(oDesign)[0]
# #         log.debug("add mesh opertion on net: %s"%net)
#         oModule.AddMeshOperation(setupName, 
#             [
#                 "NAME:Length1",
#                 "RefineInside:="    , False,
#                 "Type:="        , "LengthBased",
#                 "Enabled:="        , True,
#                 [
#                     "NAME:Assignment",
#                 ] + meshOperations,
#                 "RestrictElem:="    , False,
#                 "NumMaxElem:="        , "1000",
#                 "RestrictLength:="    , True,
#                 "MaxLength:="        , meshLength
#             ])
# 
# 
#     def setHfssExtent(self,extent = "1.5mm"):
#         #self.oEditor.SetHfssExtentsVisible(True)
#         self.oDesign.EditHfssExtents(
#             [
#             ])
# 

        
class Setups(object):

    def __init__(self,layout=None):
        
        self.layout = layout
        
            
        self._oModule = None
        self.setupDict = None
    
    def __getitem__(self, key):
        return self.SetupDict[key]
    
    def __contains__(self,key):
        return key in self.SetupDict
    
    def __len__(self):
        return len(self.SetupDict)
    
    @property
    def oModule(self):
        if not self._oModule:
            self._oModule = self.layout.oDesign.GetModule("SolveSetups")
        return self._oModule
    
    @property
    def SetupDict(self):
        if self.setupDict is None:
            self.setupDict = ComplexDict(dict([(name,Setup(name,layout=self.layout)) for name in self.getAllSetupNames()]))
            self.setupDict.setMaps(dict([(re.sub(r'[-\.\s]','_',pin),pin) for pin in self.setupDict.Keys]))
        return self.setupDict
    
    @property
    def All(self):
        return self.SetupDict
    
    def refresh(self):
        self.setupDict = None
    
    def add(self,name,solutionType = "HFSS"):
        if name in self.getAllSetupNames():
            log.info('setupName "%s" exist, will be not add'%name)
            oModule = self.layout.oDesign.GetModule("SolveSetups")
            self.layout.Log.info('setupName "%s" exist, will be remove first.'%name)
            oModule.Delete(name)
            oModule.Add(["NAME:%s"%name,"SolveSetupType:=", solutionType])
            
        else:
            log.info('add setup: "%s type: %s "'%(name,solutionType))
            oModule = self.layout.oDesign.GetModule("SolveSetups")
            oModule.Add(["NAME:%s"%name,"SolveSetupType:=", solutionType])
        
        #refresh setupDict
        self.setupDict = None
        return self.SetupDict[name]
    

    def getByName(self,name):
        if name in self.getAllSetupNames():
            return Setup(name)
        else:
            log.exception('setupName "%s" not exist'%name)
    
    def getAllSetups(self):
        return self.SetupDict.Values
#         return [Setup(name) for name in self.getAllSetupNames()]
    
    def getAllSetupNames(self):
        oModule = self.layout.oDesign.GetModule("SolveSetups")
        return oModule.GetSetups()
    
    def analyzeAll(self):
        #Analyze Nominal and optimetircs
        self.layout.oDesign.AnalyzeAll()
        #self.layout.oDesign.AnalyzeAllNominal()
        
