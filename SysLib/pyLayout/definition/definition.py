#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410

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
    


    def __init__(self, name = None,array = None,layout = None,manager=""):
        self.name = name
        self._manager = manager
        self._array = array
#         self._oDefinitionManager = None

        self.layout = layout
        self.maps = {}
        
            
    def __getitem__(self, key):
        return self.Info[key]
    
    def __setitem__(self, key,value):
        self.Info[key] = value
        self.update()

    def __getattr__(self,key):

        if key in ["layout","name","_array","_manager","maps","parsed"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]

    def __setattr__(self, key, value):
        if key in ["layout","name","_array","_manager","maps","parsed"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value

    def __repr__(self):
        return "%s Object: %s"%(self.__class__.__name__,self.Name)

    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)
    
    @property
    def Props(self):
        propKeys = self.Info.Keys
        
        if self.maps:
            propKeys += self.maps.keys()
             
        return propKeys

    @property
    def oDefinitionManager(self):
        return self.layout.oProject.GetDefinitionManager()
    
    @property
    def oManager(self):
        return self.oDefinitionManager.GetManager(self._manager)
        
    @property
    def Info(self):
        if not self._array:
            self.parse()
        return self._array
        

    def parse(self,force = False):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if self.parsed and not force:
            return
        
        datas = self.oManager.GetData(self.name)
        if datas:
            self._array = ArrayStruct(tuple2list(datas),maps=self.maps)
        else:
            self._array = []
            
        self.parsed = True
    
    
    def update(self):
        self.oManager.Edit(self.Name,self.Info.Array)
        self.parse()


    
class Definitions(object):

    def __init__(self,layout = None,definitionCalss = Definition):
        self.layout = layout
        self.definitionCalss = definitionCalss
            
    def __getitem__(self, key):
        return self.getByName(key)
            
    def __getattr__(self,key):
        if key in ['__get__','__set__']:
            #just for debug run
            return None
        
        try:
            return super(self.__class__,self).__getattribute__(key)
        except:
            log.debug("Layers __getattribute__ from _info: %s"%str(key))
            return self[key]
            
    @property
    def oDefinitionManager(self):
        return self.layout.oProject.GetDefinitionManager()
            
    
    def getByName(self,name):
        '''
        Args:
            name (str): material name in lib, ingor case
        Returns:
            (material): material object of material name
             
        Raises:
            material name not found in lib
        '''
        return self.definitionCalss(name)
