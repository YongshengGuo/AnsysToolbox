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


class ComponentDef(object):
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
        if key.lower() == "name":
            self.reName(value)
            self.layout.ComponentDefs.refresh()
            return
        
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
        return "Component Definition Object: %s"%self.Name
    
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
    
#     @Name.setter
#     def Name(self,newName):
#         self.Info.Array = "NAME:%s"%newName
#         self.update()
#         self.layout.ComponentDefs.refresh()

    
    def parse(self):
        if self.parsed:
            return
        
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oComponentManager = oDefinitionManager.GetManager("Component")
        self._array = ArrayStruct(tuple2list(oComponentManager.GetData(self.name)),maps=self.maps)
        self.parsed = True
    
    def update(self):
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oComponentManager = oDefinitionManager.GetManager("Component")
        oComponentManager.Edit(self.Name,self.Info.Array)
        self.parse()
    
    def reName(self,newName):
        self.Info.Array[0] = "NAME:%s"%newName
        self.update()
        self.layout.ComponentDefs.refresh()
        return

class ComponentDefs(object):
    

    def __init__(self,layout=None):
        self.componentDefDict = None #ComplexDict component buffer
        self.layout = layout
            
    def __getitem__(self, key):
        """
        key: str, regex, list, slice
        """
        
        if isinstance(key, int):
            return self.ComponentDefDict[key]
        
        if isinstance(key, slice):
            return self.ComponentDefDict[key]
        
        if isinstance(key, str):
            if key in self.ComponentDefDict:
                return self.ComponentDefDict[key]
            else:
                #find by 正则表达式
                lst = [name for name in self.ComponentDefDict.Keys if re.match(r"^%s$"%key,name,re.I)]
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
        
        if key in ["layout","ComponentDefDict"]:
            return object.__getattribute__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]
        
    
    def __contains__(self,key):
        return key in self.ComponentDefDict
    
    def __len__(self):
        return len(self.ComponentDefDict)
    
    @property
    def ComponentDefDict(self):
        if self.componentDefDict == None:
            oDefinitionManager = self.layout.oProject.GetDefinitionManager()
            oComponentManager = oDefinitionManager.GetManager("Component")
            self.componentDefDict  = ComplexDict(dict([(name,ComponentDef(name,layout=self.layout)) for name in oComponentManager.GetNames()]))
        return self.componentDefDict 
    
    @property
    def All(self):
        return self.ComponentDefDict
    
    @property
    def Names(self):
        return self.ComponentDefDict.Keys
    
    def refresh(self):
        self.componentDefDict  = None
        
    def push(self,name):
        self.componentDefDict.update(name,ComponentDef(name,layout=self.layout))
        
    def add(self,name):
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oComponentManager = oDefinitionManager.GetManager("Component")
        oComponentManager.Add(["NAME:%s"%name])
        self.push(name)
        