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

from ..primitive.geometry import Point,Polygen

class PadStack(object):
    '''

    Args:
    '''
    
    layoutTemp = None
    maps = {
        "DrillSize":{"Key":"psd/hle/Szs","Get":lambda x:x[0] if len(x) else None},
        }
    mapsPDS = {
        "PadSize":{"Key":"pad/Szs","Get":lambda x:x[0] if len(x) else None},
        "AntipadPadSize":{"Key":"ant/Szs","Get":lambda x:x[0] if len(x) else None},
        "ThermalPadSize":{"Key":"thm/Szs","Get":lambda x:x[0] if len(x) else None}
        }
    
    def __init__(self, name, layout=None):
        '''Initialize Pin object
        Args:
            name (str): Via name in layout
            layout (PyLayout): PyLayout object, optional
        '''
        self.name = name
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
        else:
            self.layout = self.__class__.layoutTemp

        self._array = None
        self.parsed = False

    def __getitem__(self, key):
        """
        key: str
        """
        self.parse()
        
        
        if key in self._array:
            return self._array[key] 
        
        elif key in self.layout.Layers: #if key is layerName
            layerName = self.layout.Layers[key].name
            pds = self["psd/pds"].Array
            for s in pds:
                if not isinstance(s, list):
                    continue
                
                lgm = ArrayStruct(s,maps=self.mapsPDS)
                if lgm.lay == layerName:
                    return lgm
            return None
        else:
            log.exception("key error for padstack: %s"%key)       
        

    def __setitem__(self, key,value):
        self.parse()
        self.Info[key] = value
#         self.setProp(self._array.getReallyKey(key), value)
#         self.parsed = False
        

    def __getattr__(self,key):

        if key in ["layout","name","_array","parsed"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]

    def __setattr__(self, key, value):
        if key in ["layout","name","_array","parsed"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value

    def __repr__(self):
        return "PadStack Object: %s"%self.Name
    
    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)

    @property
    def Info(self):
        if not self._array:
            self.parse()
            
        return self._array

    @property
    def Props(self):
        propKeys = list(self.Info.Keys)
        if self.maps:
            propKeys += list(self.maps.keys())
        
        return propKeys
    
    @property
    def Name(self):
        return self.name
    
    
    def parse(self):
        if self.parsed:
            return
        
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oPadstackManager = oDefinitionManager.GetManager("Padstack")
        self._array = ArrayStruct(tuple2list(oPadstackManager.GetData(self.name)),maps=self.maps)
        self.parsed = True
    
    def update(self):
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oPadstackManager = oDefinitionManager.GetManager("Padstack")
        oPadstackManager.Edit(self.Name,self.Info.Array)
        self.parse()
    
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

class PadStacks(object):
    

    def __init__(self,layout=None):
        self.padStackDict = None #ComplexDict component buffer
        self.layout = layout
            
    def __getitem__(self, key):
        """
        key: str, regex, list, slice
        """
        
        if isinstance(key, int):
            return self.PadStackDict[key]
        
        if isinstance(key, slice):
            return self.PadStackDict[key]
        
        if isinstance(key, str):
            if key in self.PadStackDict:
                return self.PadStackDict[key]
            else:
                #find by 正则表达式
                lst = [name for name in self.PadStackDict.Keys if re.match(r"^%s$"%key,name,re.I)]
                if not lst:
                    raise Exception("not found padStack: %s"%key)
                else:
                    #如果找到多个器件（正则表达式），返回列表
                    return self[lst]

        if isinstance(key, (list,tuple)):
            return [self[i] for i in list(key)]
    
    def __getattr__(self,key):
        if key in ['__get__','__set__']:
            #just for debug run
            return None
        
        if key in ["layout","PadStackDict"]:
            return object.__getattribute__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]
        
    
    def __contains__(self,key):
        return key in self.PadStackDict
    
    def __len__(self):
        return len(self.PadStackDict)
    
    @property
    def PadStackDict(self):
        if self.padStackDict == None:
            oDefinitionManager = self.layout.oProject.GetDefinitionManager()
            oPadstackManager = oDefinitionManager.GetManager("Padstack")
            self.padStackDict  = ComplexDict(dict([(name,PadStack(name,layout=self.layout)) for name in oPadstackManager.GetNames()]))
        return self.padStackDict 
    
    @property
    def All(self):
        return self.PadStackDict
    
    @property
    def Names(self):
        return self.PadStackDict.Keys
    
    def refresh(self):
        self.padStackDict  = None
        
    def push(self,name):
        self.padStackDict.update(name,PadStack(name,layout=self.layout))
        
    def add(self,name):
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oPadstackManager = oDefinitionManager.GetManager("Padstack")
        oPadstackManager.Add(["NAME:%s"%name])
        self.PadStackDict[name].appendSignalLayers() #添加默认padstack叠层信息
        self.push(name)
        