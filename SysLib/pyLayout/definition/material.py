#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410

from ..common import hfss3DLParameters
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common.unit import Unit
from ..common.common import log,tuple2list
from .definition import Definitions,Definition

import math


class Material(Definition):
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
    
    maps = {
        "DK":"permittivity",
        "DF":"dielectric_loss_tangent",
        "Cond":"conductivity",
        "Resistivity":{"Key":"conductivity","Get": lambda x:1/float(x),"Set": lambda x:str(1.0/x)},
        "k":"thermal_conductivity",
        "ur": "permeability"
        
        }
    

    def __init__(self, name = None,array = None,layout = None):
        super(self.__class__,self).__init__(name,type="Material",layout=layout)


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
            _array =  ArrayStruct(tuple2list(hfss3DLParameters.material),maps=maps)
            _array.update(ArrayStruct(datas))
        else:
            _array = ArrayStruct([])
        
#         self._info.update("self", self)
        self._info.update("Name",self.name)
        self._info.update("Array", _array)
        
        map2 = {}
        map2.update({"IsMetal":{
            "Key":"self",
            "Get":lambda s: s.isConductor()
            }})
        
        map2.update({"IsDielectric":{
            "Key":"self",
            "Get":lambda s: not s.isConductor()
            }})
        
        self._info.update("self", self)    
        self._info.setMaps(map2)
        self.maps = maps
        self.parsed = True

#     def parse(self):
#         self._array = ArrayStruct(tuple2list(hfss3DLParameters.material),maps=self.maps)
#         oMaterialManager = self.oDefinitionManager.GetManager("Material")
#         datas = oMaterialManager.GetData(self.name)
#         if not datas:
#             log.exception("Material not exist: %s"%self.name)
# 
#         self._array.update(ArrayStruct(datas))

    def update(self):
        '''
        update the material parameters to project
        All the material changeing will not update to project untill update
        
        if material not exist, will add, else will edit
        '''
        #oDefinitionManager.AddMaterial(["NAME:Material1",["NAME:PhysicsTypes","set:=", ["Electromagnetic","Thermal","Structural"]]])
        
        if self.oDefinitionManager.DoesMaterialExist(self.name):
            self.oDefinitionManager.EditMaterial(self.name,self.Array.Datas)
        else:
            self.oDefinitionManager.AddMaterial(self.Array.Datas)
            

    def isConductor(self,threshed=10000):
        
        try:
            if float(self.conductivity) < 10000:
                return False
            else:
                return True
        except:
            #conductivity is expression
            log.debug("float(conductivity) error:%s"%self.conductivity)
        
        #1e-12+2.84472e-12*Freq*(atan(Freq/70403)-atan(Freq/1.59155e+11))
        try:
            evalValue = self.layout.Variables.evalExpression(self.conductivity)
            evalValue = self.layout.Variables.EvalExpressionValue.SIValue
            if float(evalValue) < 10000:
                return False
            else:
                return True
        except:
            #conductivity is expression
            log.debug("Eval conductivity value error:%s"%self.conductivity)

        log.warning("Can't justment the material %s is counductor or not, just return False."%self.name)
        return False

    
class Materials(Definitions):

    def __init__(self,layout=None):
        super(self.__class__,self).__init__(layout, type="Material",definitionCalss=Material)
            
    def __getitem__(self, key):
        try:
            return super(self.__class__,self).__getitem__(key)
        except: 
            return self.getByName(key)
            
    def __contains__(self,key):
        #key is case-insensitive
        if super(self.__class__,self).__contains__(key):
            return True
        
        return bool(self.getByName(key))


#     @property
#     def DefinitionDict(self):
#         if self._definitionDict == None:
#             log.warning("Materials collection only has material in project, material in SysLibrary will not include in Materials collection. \
#                 But you can use Material(name) or getByName(name) to get the Material object in SysLibrary")
#             oManager = self.oDefinitionManager.GetManager("Material")
#             self._definitionDict = ComplexDict(dict([(name,Material(name,layout=self.layout)) for name in oManager.GetNames()]))
#         return self._definitionDict
    
#     @property
#     def DefinitionDict(self):
#         if self._definitionDict == None:
#             oDefinitionManager = self.layout.oProject.GetDefinitionManager()
#             oManager = oDefinitionManager.GetManager(self.type)
#             self._definitionDict  = ComplexDict(dict([(name,self.definitionCalss(name,layout=self.layout)) for name in oManager.GetNames()]))
#         return self._definitionDict
    
            
    def create(self,infoDict={},name=None,**kwargs):
        '''
        infoDict(dict): {name:copper,....}
        
        Only create the Material object, not add to layout
        '''
        ops = ComplexDict(infoDict)
        ops.updates(kwargs)
        ary = ArrayStruct(tuple2list(hfss3DLParameters.material),maps=Material.maps).copy()
        
        if name:
#             name = name
            ary.Array[0] = 'NAME:%s'%name
#             if "Name" in ops:
#                 del ops["Name"]
        else:
            name = ops["Name"]
            ary.Array[0] = 'NAME:%s'%name
        
        if "Name" in ops:
            del ops["Name"]
            
        for k in ops.Keys:
            if k in ary:
                ary[k] = str(ops[k])
            else:
                log.info("Material key '%s' ignor."%k)
                
        material = Material(name,layout=self.layout)
        material.Array = ary
#         material._info = ary
        return material
            
            
    def add(self,infoDict={},name=None,**kwargs):
        '''
        info(dict): {name:copper,....}
        if material not exist, will add, else will edit
        '''
        material = self.create(infoDict,name,**kwargs)
        material.update()
        self.push(material.name)
        return material
        
    def addHFSSDSModle(self,name,dk=4,df=0.02,f1=1e9,cond_dc=1e-12,fB=10**12/(2*math.pi)):
        '''
        Djordjevic-Sarkar Model Parameter Calculation in hfss
        WA<<W1=> f1>>fB
        fB default 10^12/(2*pi)
        '''
        # K = f"({dk} * {df} - {cond_dc} / (2 * pi * {freqA} * e0)) / atan({freqB} / {freqA})"
        w1 = 2*math.pi*f1
        wB = 2*math.pi*fB
        e0 = 8.854187817e-12  
        
        K = (dk*df-cond_dc/(w1*e0))/math.atan(wB/w1)
        e_infi = dk-0.5*K*math.log(wB**2/w1**2+1)
        e_delta = 10*df*e_infi
        fA = fB/math.exp(e_delta/K)
        log.info("Djordjevic-Sarkar Model Parameter:\n",
                 "e_infi:%s "%e_infi,
                 "e_delta:%s "%e_delta,
                 "fA:%s "%fA,
                 "fB:%s "%fB
                 )
        
        e_freq = "{e_infi}+{K}/2*ln(({fB}**2+freq**2)/({fA}**2+freq**2))".format(e_infi=e_infi,K=K,fB=fB,fA=fA)
        cond_freq = "{cond_dc}+2*pi*freq*e0*{K}*(atan(freq/{fA})-atan(freq/{fB}))".format(cond_dc=cond_dc,K=K,fB=fB,fA=fA)
        log.info("Djordjevic-Sarkar Model Parameter:\n",
                 "DK:%s\n"%e_freq,
                 "Conductivity:%s"%cond_freq
                 )
        self.add({
            "Name":name,
            "DK":e_freq,
            "Cond":cond_freq
            })
        
    def addHFSSDSModle2(self,name,dk=4,df=0.02,f1=1e9,cond_dc=1e-12,fB=10**12/(2*math.pi)):
        '''
        Djordjevic-Sarkar Model Parameter Calculation in hfss
        WA<<W1=> f1>>fB
        fB default 10^12/(2*pi)
        '''
        # K = f"({dk} * {df} - {cond_dc} / (2 * pi * {freqA} * e0)) / atan({freqB} / {freqA})"
        w1 = 2*math.pi*f1
        wB = 2*math.pi*fB
        e0 = 8.854187817e-12  
        
        K = (dk*df-cond_dc/(w1*e0))/math.atan(wB/w1)
        e_infi = dk-0.5*K*math.log(wB**2/w1**2+1)
        e_delta = 10*df*e_infi
        fA = fB/math.exp(e_delta/K)
        log.info("Causal material set fA as: %s"%fA)
        self.addStdDSModel(name,e_infi,e_delta,fA,fB,cond_dc)


    def addStdDSModel(self,name,e_infi,e_delta,fA,fB,cond_dc=1e-12):
        wA = 2*math.pi*fA
        wB = 2*math.pi*fB
        e0 = 8.854187817e-12  
        
        log.info("Djordjevic-Sarkar Model Parameter:\n",
                 "e_infi:%s "%e_infi,
                 "e_delta:%s "%e_delta,
                 "fA:%s "%fA,
                 "fB:%s "%fB
                 )
        
        cer = "{e_infi}+{e_delta}/ln({wB}/{wA})*ln(({wB}+1j*2*pi*freq)/({wA}+1j*2*pi*freq))+{cond_dc}/(1j*2*pi*freq*e0)".format(
            e_infi=e_infi,e_delta=e_delta,wB=wB,wA=wA,cond_dc=cond_dc
            )
        dk = "re({cer})".format(cer=cer)
        df = "-im({cer})/re({cer})".format(cer=cer)
        log.info("Djordjevic-Sarkar Model Parameter:\n",
                 "DK:%s\n"%dk,
                 "DF:%s"%df
                 )
        self.add({
            "Name":name,
            "DK":dk,
            "DF":df
            })
        
    
    def getByName(self,name):
        '''
        Args:
            name (str): material name in lib, ingor case
        Returns:
            (material): material object of material name
             
        Raises:
            material name not found in lib
        '''
#         oDefinitionManager = self.layout.oProject.GetDefinitionManager()
#         if not oDefinitionManager.DoesMaterialExist(name): #only for project material
#             raise Exception("Material not definition: %s"%name)
#         oMaterialManager = oDefinitionManager.GetManager("Material")
        rst = super(self.__class__,self).getByName(name)
        if rst:
            return rst
        else:
            temp =  Material(name)
            if temp.Array.Datas:
                return temp
            else:
                return None
            
