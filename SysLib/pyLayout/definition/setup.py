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
from .definition import Definitions,Definition
from ..common.common import log

class Sweep(Definition):
    
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
    
    
    def __init__(self,sweepName = None,setupName=None,layout=None):
        super(self.__class__,self).__init__(sweepName,type="Sweep",layout=layout)
        self._info.update("sweepName",sweepName)
        self._info.update("setupName",setupName)
        
    @property
    def SolutionName(self):
        return "%s:%s"%(self.Info.setupName,self.Info.sweepName)
    
    @property
    def oModule(self):
        return self.oDesign.GetModule("SolveSetups")

    
    @property
    def oManager(self):
        return self.oModule

    
    def parse(self,force = False):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if self.parsed and not force:
            return
        
        log.debug("parse primitive: %s"%self.name)
        SolveSetupType =  self.layout.Setups[self._info.setupName].SolveSetupType 
        
        maps = {}
        if SolveSetupType== "HFSS":
            maps = self.mapsForHFSS
        elif SolveSetupType== "SIwave":
            maps = self.mapsForSIwave
        else:
            log.error("Unknow setup type:%s"%self._info.setupName)
 
        datas = self.oModule.GetSweepInfo(self._info.setupName,self._info.sweepName)
        if datas:
            _array = ArrayStruct(tuple2list(datas),maps)
        else:
            _array = []
            
        self._info.update("Name",self.name)
        self._info.update("Array", _array)
#         self.__class__.maps = maps
            
        self.parsed = True


    def update(self):
#         self.oManager.EditSweep(self.setupName,self.Array.Datas)
        self.oModule.EditSweep(self.setupName,self.sweepName,self.Array.Datas)
        self.parse()

    def delete(self):
        self.oModule.DeleteSweep(self.Info.setupName,self.Info.sweepName)
    
    
    def analyze(self):
        self.oModule.AnalyzeSweep(self.Info.setupName,self.Info.sweepName)
    

class Sweeps(Definitions):
 
    def __init__(self,layout=None,setupName = None):
        super(self.__class__,self).__init__(layout, type="Sweep",definitionCalss=Sweep)
        self.setupName = setupName
     
    @property
    def oModule(self):
        return self.layout.oDesign.GetModule("SolveSetups")

     
    @property
    def DefinitionDict(self):
        if self._definitionDict is None:
            self._definitionDict = ComplexDict(dict([(name,Sweep(name,self.setupName,layout=self.layout)) for name in self.oModule.GetSweeps(self.setupName)]))
#             self._definitionDict.setMaps(dict([(re.sub(r'[-\.\s]','_',pin),pin) for pin in self._definitionDict.Keys]))
        return self._definitionDict

    def _getSweeps(self):
#         sweepDict = {}
#         for name in self.oModule.GetSweeps(self.setupName):
#             sweepDict[name] = Sweep(name,self.setupName,layout=self.layout)
        
        return ComplexDict(dict([(name,Sweep(name,self.setupName,layout=self.layout)) for name in self.oModule.GetSweeps(self.setupName)]))

class Setup(Definition):

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
        
        super(self.__class__,self).__init__(name,type="Setup",layout=layout)

    
    @property
    def oModule(self):
        return self.oDesign.GetModule("SolveSetups")

    
    @property
    def oManager(self):
        return self.oModule
    
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
#             self._info = None
#             return None
#         
#         datas = self.Info # ArrayStruct(self.oModule.GetSetupData(self.name))
#         datas.set(path,value)
#         self.oModule.Edit(self.name,datas.Array)
#         #update Info
#         self._info = None
    
    def parse(self,force = False):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if self.parsed and not force:
            return
        
        log.debug("parse primitive: %s"%self.name)
        self._info = ComplexDict()
        
    
        datas = self.oModule.GetSetupData(self.name)
        if datas:
            _array = ArrayStruct(tuple2list(datas),self.maps)
        else:
            _array = []
            
            
        self._info.update("Array", _array)
        
        self._info.update("Name",self.name)
        maps = {}
        maps.update({"Sweeps":{
            "Key":"Name",
            "Get":lambda k: Sweeps(layout=self.layout,setupName=self.name) #[Sweep(k,sweepName) for sweepName in self.oModule.GetSweeps(self.name)]
            }})
        
        self._info.setMaps(maps)
            
        self.parsed = True


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
        log.info("Get net information ... ")
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

        
class Setups(Definitions):

    def __init__(self,layout=None):
        super(self.__class__,self).__init__(layout, type="Setup",definitionCalss=Setup)
    
    @property
    def oModule(self):
        if not self._manager:
            self._manager = self.layout.oDesign.GetModule("SolveSetups")
        return self._manager
    
    @property
    def DefinitionDict(self):
        if self._definitionDict is None:
            oModule = self.layout.oDesign.GetModule("SolveSetups")
            self._definitionDict = ComplexDict(dict([(name,Setup(name,layout=self.layout)) for name in oModule.GetSetups()]))
#             self._definitionDict.setMaps(dict([(re.sub(r'[-\.\s]','_',pin),pin) for pin in self._definitionDict.Keys]))
        return self._definitionDict
    
    
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
        
        #refresh _definitionDict
        self._definitionDict = None
        return self.DefinitionDict[name]
    

    def getByName(self,name):
        if name in self.getAllSetupNames():
            return Setup(name)
        else:
            log.exception('setupName "%s" not exist'%name)
    
    def getAllSetupNames(self):
        oModule = self.layout.oDesign.GetModule("SolveSetups")
        return oModule.GetSetups()
    
    def analyzeAll(self):
        #Analyze Nominal and optimetircs
        self.layout.oDesign.AnalyzeAll()
        #self.layout.oDesign.AnalyzeAllNominal()
        
