#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230828


'''
used to get padstak information

'''



import re

from ..common import hfss3DLParameters
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common.unit import Unit
from ..common.common import log,tuple2list
from .definition import Definitions,Definition
from ..primitive.geometry import Point,Polygen

class PadStack(Definition):
    '''

    Args:
    '''
    
    maps = {
        "DrillSize":{"Key":"psd/hle/Szs","Get":lambda x:x[0] if len(x) else None},
        }
    mapsPDS = {
        "PadSize":{"Key":"pad/Szs","Get":lambda x:x[0] if len(x) else None},
        "AntipadPadSize":{"Key":"ant/Szs","Get":lambda x:x[0] if len(x) else None},
        "ThermalPadSize":{"Key":"thm/Szs","Get":lambda x:x[0] if len(x) else None}
        }
    
    def __init__(self, name = None,layout = None):
        super(self.__class__,self).__init__(name,type="Padstack",layout=layout)


    def parse(self,force = False):
        super(self.__class__,self).parse(force)
        
        pds = self._info.Array["psd/pds"]
        for pd in pds.Datas:
            if not isinstance(pd, list):
                continue
            lgm = ArrayStruct(pd,maps=self.mapsPDS)
            self._info.update(lgm.lay, lgm)

    
    def appendLayer(self,layerName,update=True):
        self.Info.append("psd/pds",
            [
                "NAME:lgm",
                "lay:=", layerName,
                "id:=", 1, #self.layout.layers[layerName].ID,
                "pad:=", ["shp:=", "No","Szs:=", [],"ply:=", [],"X:=", "0mil","Y:=", "0mil","R:=", "0deg"],
                "ant:=", ["shp:=", "No","Szs:=", [],"ply:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "thm:=", ["shp:=", "No","Szs:=", [],"ply:=", [],"X:=", "0mm","Y:=", "0mm","R:=", "0deg"],
                "X:=", "0",
                "Y:=", "0",
                "dir:=", "No"
            ])
        if update:
            self.update()
    
    def appendSignalLayers(self):
        if len(self["psd/pds"])>1:
            self["psd/pds"] = ["NAME:pds"]
        
        for layerName in self.layout.Layers.ConductorLayerNames:
            self.appendLayer(layerName,update=False)
            
        self.update()
        

    def place(self,center,layerUpper,layerLower = None,isPin = False):
        '''
        Center: [x,y], str value
        #Return Value: Returns the name of the created via
        '''
        if len(center)!=2:
            log.exception("Center must have length 2")
            
        if not layerLower:
            layerLower = layerUpper
        
        name = self.layout.oEditor.CreateVia(
            [
                "NAME:Contents",
#                 "name:="        , "pad_0000",
                "ReferencedPadstack:="    , self.Name,
                "vposition:="        , ["x:=", center[0],"y:=",center[1]],
                "vrotation:="        , ["0deg"],
                "overrides hole:="    , False,
                "hole diameter:="    , ["1mm"],
                "Pin:="            , isPin,
                "highest_layer:="    , layerUpper,
                "lowest_layer:="    , layerLower
            ])
        
        if isPin:
            self.layout.Pins.push(name)
        else:
            self.layout.Vias.push(name)
        
        return name

class PadStacks(Definitions):
    
    def __init__(self,layout=None):
        super(self.__class__,self).__init__(layout, type="Padstack",definitionCalss=PadStack)

     
    def add(self,name):
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oPadstackManager = oDefinitionManager.GetManager("Padstack")
        oPadstackManager.Add(["NAME:%s"%name])
        self.DefinitionDict[name].appendSignalLayers() #添加默认padstack叠层信息
        self.push(name)
        