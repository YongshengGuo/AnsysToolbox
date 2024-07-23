#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20240317

import re
from collections import Iterable
from ..common import hfss3DLParameters
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common.unit import Unit
from ..common.common import log

from .geometry import Point

'''
this a base class for privitives of : 
        'pin', 'via', 'rect', 'arc', 'line', 'poly', 
        'plg', 'circle void', 'line void', 'rect void', 'poly void', 'plg void', 'text', 'cell', 
        'Measurement', 'Port', 'Port Instance', 'Port Instance Port', 'Edge Port', 'component', 'CS', 'S3D', 'ViaGroup'
        
It 's not recommand to initial Primitive or Primitives object redirect.
'''


class Primitive(object):
    '''_summary_

    Args:
        object (_type_): _description_
    '''

    layoutTemp = None
    
    
    def __init__(self, name, layout=None):
        '''Initialize Pin object
        Args:
            name (str): poly name in layout
            layout (PyLayout): PyLayout object, optional
        '''
        self.name = name
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
        else:
            self.layout = self.__class__.layoutTemp

        self._info = None
        self.maps = {}
        self.parsed = False

    def __getitem__(self, key):
        """
        key: str
        """
        return self.get(key)


    def __setitem__(self,key,value):
        self.set(key,value)

        

    def __getattr__(self,key):

        if key in ["layout","name","_info","maps","parsed"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]
        

    def __setattr__(self, key, value):
        if key in ["layout","name","_info","maps","parsed"]:
            object.__setattr__(self,key,value)
        else:
            log.debug("get property '%s' from dict."%key)
            self[key] = value

    def __repr__(self):
        return "%s Object: %s"%(self.__class__.__name__,self.Name)
    
    def __contains__(self,key):
        return key in self.Info
    
    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)

    @property
    def Info(self):
        if not self._info:
            self.parse()
            
        return self._info

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
    def Type(self):
        return self.getProp("Type")
    
    @property
    def Collection(self):
        return self.layout[self.getProp("Type")+"s"]
    
    def parse(self,force = False):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if self.parsed and not force:
            return
        
        log.debug("parse primitive: %s"%self.name)
        self._info = ComplexDict()
        maps = self.maps
        self._info.update("Name",self.name) #add name to Info
        
        #--- for BaseElementTab peoperty
        properties = self.layout.oEditor.GetProperties("BaseElementTab",self.Name)
        self._info.update("Properties",properties)
        for prop in properties:
            self._info.update(prop,None) #here give None value. get property value when used to improve running speed
            if " " in prop:
                maps.update({prop.replace(" ",""):prop}) #map property with space characters
                
            if re.match(r"Pt(\d+|s)$",prop,re.IGNORECASE): 
                self._info.update("Pts",None)
  
        self._info.setMaps(maps)
        self.parsed = True


    def get(self,key):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if not self.parsed:
            self.parse()
  
        
        if key in self._info and self._info[key] != None: # Map value or already have value
            return self._info[key]
        
        if not isinstance(key, str): #key must string
            log.exception("Property error: %s->%s"%(self.name,str(key)))
        
        realKey = self._info.getReallyKey(key)
        if re.match(r"Pt(\d+|s)$",realKey,re.IGNORECASE) or realKey in ["Center","Pt A","Pt B","Location"]: 
            
            self._info.update(realKey,self.getPoint(realKey))
            return self._info[realKey]
        
        if realKey in self._info.Properties:  #value is None
            self._info.update(realKey,self.getProp(realKey))
            return self._info[realKey]
        else:
            log.exception("Property error: %s->%s"%(self.name,key))
    
    def set(self,key,value):
        '''
        mapping key must not have same value with maped key.
        '''
        
        
        if not self.parsed:
            self.parse()
        
        if not isinstance(key, str): #key must string
            log.exception("Property error: %s->%s"%(self.name,str(key)))
        
#         realKey = self._info.getReallyKey(key) #don't use mapkey
        realKey = key  #don't use mapkey
           
        if re.match(r"Pt(\d+|s)$",key,re.IGNORECASE) or key in ["Center","Pt A","Pt B","Location"]: 
            self.setPoint(key, value)
            self.parsed = False #refresh
            
        elif key in self._info.Properties: 
            self.setProp(realKey, value)
            self._info[realKey] = value
#             self.parsed = False #refresh
            
        elif key in self._info:
            log.warning("Attribute values will not take effect in layout: %s:%s"%(key,value))
            self._info[realKey] = value
        
        else:
            log.exception("Property error: %s->%s"%(self.name,key))

    def getProp(self,prop):
        return self.layout.oEditor.GetPropertyValue("BaseElementTab",self.Name,prop)

    def setProp(self,prop,value):
        
        if re.match(r"Pt\s*[\dAB]+$",prop): #set Points: Pt0,Pt1, Pt A, Pt B, support expression
            self.setPoint(prop, value)
        else:
            self.layout.oEditor.SetPropertyValue("BaseElementTab",self.name, prop,value)

        
    def setPoint(self,ptName,value):
        '''
        value: list,tuple,"x,y",Point, 3DL Point
        '''
#         key = self._info.getReallyKey(ptName)
        
        key = ptName
        if re.match(r"Pt\d+$",key) or key in ["Center","Pt A","Pt B","Location"]:
            pt = Point(value)
            self.layout.oEditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:BaseElementTab",
                        [
                            "NAME:PropServers", 
                            self.Name
                        ],
                        [
                            "NAME:ChangedProps",
                            [
                                "NAME:%s"%ptName,
                                "X:=", pt.X,
                                "Y:=", pt.Y
                            ]
                        ]
                    ]
                ])
            return None
        
        if key.lower() == "pts" and isinstance(value, (list,tuple)):
            for i in range(len(value)):
                self.setPoint("Pt%s"%i, value[i])
                
            return None             
        
        log.exception("property or value error: %s %s"%(ptName,str(value)))
        
    def getPoint(self,ptName):
        #add unit for pt\d+ or pt [AB]
        
        key = self._info.getReallyKey(ptName)
        if re.match(r"Pt\d+$",key) or key in ["Center","Pt A","Pt B","Location"]:
            ptValue = self.layout.oEditor.GetPropertyValue("BaseElementTab",self.Name,key)
            return Point(["%s%s"%(c.strip(),self.layout.unit) for c in ptValue.split(",")])
        
        if key.lower() == "pts":
            pts = []
            for p in self._info.Keys:
                if re.match(r"Pt\d+", p):
                    pts.append(self.getPoint(p))
            return pts
        
        log.exception("property error: %s"%ptName)
  

    def delete(self):
        self.layout.oEditor.Delete([self.Name])
        self.layout.Shapes.pop(self.Name)

    def update(self):
        self._info = None #delay update
#         self.parse()


class Primitives(object):
    

    def __init__(self,layout=None,type="*",primitiveClass=Primitive):
        self._objectDict = None #ComplexDict component buffer
        self.layout = layout
        self.type = type
        self.primitiveClass = primitiveClass
   
            
    def __getitem__(self, key):
        """
        key: str, regex, list, slice
        """
        
        if isinstance(key, int):
            return self.ObjectDict[key]
        
        if isinstance(key, slice):
            return self.ObjectDict[key]
        
        if isinstance(key, str):
            if key in self.ObjectDict:
                return self.ObjectDict[key]
            elif re.match(r".*[\*\.\?\+\{\}\|].*",key,re.I): #正则表达式
                #find by 正则表达式
                lst = [name for name in self.ObjectDict.Keys if re.match(r"^%s$"%key,name,re.I)]
                if not lst:
                    return []
#                     raise Exception("not found component: %s"%key)
                else:
                    #如果找到多个器件（正则表达式），返回列表
                    return self[lst]
            else:
                raise Exception("not found component: %s"%key)

        if isinstance(key, (list,tuple,Iterable)):
            return [self[i] for i in list(key)]
    
    def __getattr__(self,key):
        if key in ['__get__','__set__']:
            #just for debug run
            return None
        if key in ["layout","_objectDict","type","primitiveClass"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]
    
    def __contains__(self,key):
        return key in self.ObjectDict
    
    def __len__(self):
        return len(self.ObjectDict)
    
    def __repr__(self):
        return "%s Objects collection"%(self.type)
    
    @property
    def ObjectDict(self):
        '''
        FindObjects
        "Type" to search by object type.
        Valid <value> strings for this type include: 'pin', 'via', 'rect', 'arc', 'line', 'poly', 
        'plg', 'circle void', 'line void', 'rect void', 'poly void', 'plg void', 'text', 'cell', 
        'Measurement', 'Port', 'Port Instance', 'Port Instance Port', 'Edge Port', 'component', 'CS', 'S3D', 'ViaGroup'
        '''
        
        if self._objectDict is None:
            self._objectDict  = ComplexDict(dict([(p,self.primitiveClass(p,layout=self.layout)) for p in 
                                self.layout.oEditor.FindObjects('Type', self.type)
                                ]))
        return self._objectDict 
    
    @property
    def All(self):
        return self.ObjectDict.Values
    
    @property
    def Type(self):
        return self.type
    
    @property
    def NameList(self):
        return self.ObjectDict.Keys
    
    def filter(self, func):
        return dict(filter(func,self.ObjectDict.items()))
    

    def filterByLayer(self,layerName):
        '''
        type: [] or Poly Object
        '''
        objsLayerAll = self.layout.oEditor.FindObjects('Layer',self.layout.layers.getRealLayername(layerName))
        return self.filter(lambda k,v:k in objsLayerAll)
        
        
#         objsLayer = []
#         objsLayerAll = self.layout.oEditor.FindObjects('Layer',self.layout.layers.getRealLayername(layerName))
#         objsLayerNames = list(filter(lambda x:x in objsLayerAll, self.NameList))
#         return self[objsLayerNames]
    
        
    def refresh(self):
        self._objectDict  = None

        
    def push(self,name):
        self._objectDict.update(name,self.primitiveClass(name,layout=self.layout))
    
    def pop(self,name):
        del self._objectDict[name]
        

    def getByName(self,name):
        '''
        Args:
            name (str): component name in layout, ingor case
        Returns:
            (Component): Component object of name
             
        Raises:
            name not found on layout
        '''
        if name in self.ObjectDict:
            return self.ObjectDict[name]
        
        log.info("not found component: %s"%name)
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
    
class Objects3DL(Primitives):

    def __init__(self,layout=None,types=".*"):
        self._objectDict = None #ComplexDict component buffer
        self.layout = layout
        self.types = types #str, list, regex
            
    def __getitem__(self, key):
        """
        key: str, regex, list, slice
        """
        
        if isinstance(key, int):
            return self.ObjectDict[key]
        
        if isinstance(key, slice):
            return self.ObjectDict[key]
        
        if isinstance(key, str):
            if key in self.ObjectDict:
                return self.ObjectDict[key]
            else:
                #find by 正则表达式
                lst = [name for name in self.ObjectDict.Keys if re.match(r"^%s$"%key,name,re.I)]
                if not lst:
                    raise Exception("not found component: %s"%key)
                else:
                    #如果找到多个器件（正则表达式），返回列表
                    return self[lst]

        if isinstance(key, (list,tuple,Iterable)):
            return [self[i] for i in list(key)]
    
    def __getattr__(self,key):
        if key in ['__get__','__set__']:
            #just for debug run
            return None
        if key in ["layout","_objectDict","types"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]
    
    def __repr__(self):
        return "%s Objects collection"%(str(self.types))

    @property
    def ObjectDict(self):
        '''
        FindObjects
        "Type" to search by object type.
        Valid <value> strings for this type include: 'pin', 'via', 'rect', 'arc', 'line', 'poly', 
        'plg', 'circle void', 'line void', 'rect void', 'poly void', 'plg void', 'text', 'cell', 
        'Measurement', 'Port', 'Port Instance', 'Port Instance Port', 'Edge Port', 'component', 'CS', 'S3D', 'ViaGroup'
        '''
        types = []
        if isinstance(self.types, str):
            types = [self.types]
        elif isinstance(self.types,(list,tuple)):
            types = list(self.types)
        else:
            log.exception("type error %s"%str(self.types))
        
        objTypes = []
        for t in types:
            for t2 in self.layout.objTypes:
                if re.match(r"^%s?$"%t,t2,re.I):
                    objTypes.append(t2)
            
            
#             objTypes += [name for name in self.layout.objTypes if re.match(r"^%s?$"%t,name,re.I)]
        
        self.types = objTypes
        if len(objTypes)<1:
            return []
        
        if self._objectDict is None:
            self._objectDict = ComplexDict()
            for typ in self.types:
                try:
                    objs = self.layout[typ+"s"]
                except:
                    log.exception("%s not in layout deifiniton"%typ)
                
                self._objectDict._dict.update(objs.ObjectDict._dict)

        return self._objectDict 
