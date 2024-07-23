#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410

import re

try:
    from collections import Iterable
except:
    from collections.abc import Iterable

from ..common import hfss3DLParameters
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common.unit import Unit
from ..common.common import log,tuple2list

import math


class Definition(object):
    '''
    oMaterialManager.GetData()
    ['NAME:copper', 'CoordinateSystemType:=', 'Cartesian', 'BulkOrSurfaceType:=', 1, 
    ['NAME:PhysicsTypes', 'set:=', ['Electromagnetic', 'Thermal',"Structural"]], 
    'permittivity:=', '0.999991', 
    "permeability:="    , "1",
    "conductivity:="    , "0",
    "dielectric_loss_tangent:=", "0",
    "magnetic_loss_tangent:=", "0"
    'thermal_conductivity:=', '0', 
    'mass_density:=', '0', 
    'specific_heat:=', '0']
    '''
    
    layoutTemp = None
    maps = {}
    
    def __init__(self, name,type,layout=None):
        '''Initialize Pin object
        Args:
            name (str): Via name in layout
            layout (PyLayout): PyLayout object, optional
        '''
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
        else:
            self.layout = self.__class__.layoutTemp
            
        self.name = name
        self.type = type
        
        self._info = ComplexDict()
        self.parsed = False

    def __getitem__(self, key):
        """
        key: str
        """
        self.parse()
        
        #for multi-level key
        keyList = re.split(r"[\\/]", key,maxsplit = 1)
        keyList = list(filter(lambda k:k.strip(),keyList)) #filter empty key
        if len(keyList)>1:
            return self[keyList[0]][keyList[1]]
        
        
        if key in self._info.Array:
            return self._info.Array[key] 
        
        elif key in self._info:
            return self._info[key] 

        else:
            log.exception("key error for %s: %s"%(self.type,key))       
        

    def __setitem__(self, key,value):
        self.parse()
        
        #for multi-level key
        keyList = re.split(r"[\\/]", key,maxsplit = 1)
        keyList = list(filter(lambda k:k.strip(),keyList)) #filter empty key
        if len(keyList)>1:
            self[keyList[0]][keyList[1]] = value

        if key in self._info.Array:
            self._info.Array[key] = value
            self.update()
            
        elif key in self._info:
            self._info[key] = value

        else:
            log.exception("key error for %S: %s"%(self.type,key))       
        

    def __getattr__(self,key):

        if key in ["layout","name","_info","parsed","type","maps"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]

    def __setattr__(self, key, value):
        if key in ["layout","name","_info","parsed","type","maps"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value

    def __repr__(self):
        return "%s Object: %s"%(self.__class__.__name__ ,self.name)
    
    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)

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
    def Props(self):
        propKeys = list(self.Info.Keys) + list(self.Array.Keys)
        
        if self.Info.maps:
            propKeys += self.Info.maps.keys()
            
        try:
            propKeys +=  self.Info.Array.Keys
            propKeys +=  self.Info.Array.maps.keys()
        except:
            pass
             
        return propKeys

    @property
    def oDefinitionManager(self):
        return self.layout.oProject.GetDefinitionManager()
    
    @property
    def oManager(self):
        return self.oDefinitionManager.GetManager(self.type)
        
    @property
    def Info(self):
        self.parse()
        return self._info
    
    @property
    def Array(self):
        self.parse()
        return self._info.Array
        

        
    def parse(self,force = False):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if self.parsed and not force:
            return
        
        log.debug("parse definition: %s"%self.name)
        maps = self.maps.copy()
        datas = self.oManager.GetData(self.name)
        if datas:
            _array = ArrayStruct(tuple2list(datas),maps)
        else:
            _array = ArrayStruct([])
        
#         self._info.update("self", self)    
        self._info.update("Name",self.name)
        self._info.update("Array", _array)
        
        self.maps = maps
        self.parsed = True
    
    
    def update(self):
        self.oManager.Edit(self.Name,self.Array.Datas)
        self.parse()


    
class Definitions(object):

    def __init__(self,layout = None,type=None,definitionCalss = Definition):
        self.layout = layout
        self.definitionCalss = definitionCalss
        self.type = type
        self._definitionDict = None
            
    def __getitem__(self, key):
        
        if isinstance(key, int):
            return self.DefinitionDict[key]
        
        if isinstance(key, slice):
            return self.DefinitionDict[key]
        
        if isinstance(key, str):
            
#             #for multi-level key
#             keyList = re.split(r"[\\/]", key,maxsplit = 1)
#             keyList = list(filter(lambda k:k.strip(),keyList)) #filter empty key
#             if len(keyList)>1:
#                 return self[keyList[0]][keyList[1]]
            
            if key in self.DefinitionDict:
                return self.DefinitionDict[key]
            else:
                #find by 正则表达式
                lst = [name for name in self.DefinitionDict.Keys if re.match(r"^%s$"%key,name,re.I)]
                if not lst:
                    raise Exception("not found %s: %s"%(self.type,key))
                else:
                    #如果找到多个器件（正则表达式），返回列表
                    return self[lst]

        if isinstance(key, (list,tuple,Iterable)):
            return [self[i] for i in list(key)]
        
        raise Exception("not found %s: %s"%(self.type,key))
        
            
    def __getattr__(self,key):
        if key in ['__get__','__set__']:
            #just for debug run
            return None
#         print("%s  __getattribute__ from _info: %s"%str(self.__class__.name,key))
        try:
            return super(self.__class__,self).__getattribute__(key)
        except:
            log.debug("%s  __getattribute__ from _info: %s"%(self.__class__.__name__,key))
            return self[key]
            
    def __contains__(self,key):
        return key in self.DefinitionDict
    
    def __len__(self):
        return len(self.DefinitionDict)
    
    def __repr__(self):
        return "%s Objects Definitios:"%(self.type)
            
            
    @property
    def oDefinitionManager(self):
        return self.layout.oProject.GetDefinitionManager()
            
    
    @property
    def DefinitionDict(self):
        if self._definitionDict == None:
            oDefinitionManager = self.layout.oProject.GetDefinitionManager()
            oManager = oDefinitionManager.GetManager(self.type)
            self._definitionDict  = ComplexDict(dict([(name,self.definitionCalss(name,layout=self.layout)) for name in oManager.GetNames()]))
        return self._definitionDict
    
    @property
    def All(self):
        return self.DefinitionDict.Values
    
    @property
    def Count(self):
        return len(self)
    
    @property
    def Type(self):
        return self.type
    
    @property
    def NameList(self):
        return list(self.DefinitionDict.Keys)
    
    def filter(self, func):
        return dict(filter(func,self.ObjectDict.items()))
    
    def refresh(self):
        self._definitionDict  = None
        
    def push(self,name):
        self.DefinitionDict.update(name,self.definitionCalss(name,layout=self.layout))
    
    def pop(self,name):
        del self.DefinitionDict[name]
        
        
    def getByName(self,name):
        '''
        Args:
            name (str): component name in layout, ingor case
        Returns:
            (Component): Component object of name
             
        Raises:
            name not found on layout
        '''
        if name in self.DefinitionDict:
            return self.DefinitionDict[name]
        
        log.info("not found %s: %s"%(self.type,name))
        return None
    
    def getUniqueName(self,prefix=""):
        
        if prefix == None:
            prefix = "%s_"%self.type
            
        for i in range(1,100000):
            name = "%s%s"%(prefix,i)
            names = self.NameList
            if name in names:
                i += 1
            else:
                break
        return name
        