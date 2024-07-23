#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410

'''
    ArrayStruct used to manage string array struct in HFSS/3DL/SIwave or other AEDT tools, like setup information as below
    
    ```python
    datas = [
        "NAME:HFSS_Setup",
        [
            "NAME:Properties",
            "Enable:="        , "true"
        ],
        "CustomSetup:="        , False,
        "AutoSetup:="        , False,
        "SliderType:="        , "Balanced",
        "SolveSetupType:="    , "HFSS",
        "PercentRefinementPerPass:=", 30,
        "MinNumberOfPasses:="    , 1,
        "MinNumberOfConvergedPasses:=", 1,
        "UseDefaultLambda:="    , True,
        "UseMaxRefinement:="    , False,
        "MaxRefinement:="    , 1000000,
        ...
    ```
    
    Examples:
        >>> arys = ArrayStruct(datas)
    
        Get data "SolveSetupType"
        >>> arys.get("SolveSetupType")
        >>> arys["SolveSetupType"]
        
        Get data "Enable"
        >>> arys.get("Properties/Enable")
        >>> arys["Properties/Enable"]
    
        Set data "SolveSetupType"
        >>> arys.set("SolveSetupType","HFSS")
        >>> arys[SolveSetupType"] = "HFSS"
        
        Set data "Enable"
        >>> arys.set("Properties/Enable","true")
        >>> arys["Properties/Enable"] = "true"
        
        Get sub Array. if self[] value is list, it will return a sub ArrayStruct of the new list value.
        >>> arys["Properties"]
        But get() will return the list, will not generate new ArrayStruct
        >>>arys.get("Properties")
        
        Set a new list value to "Properties"
        >>> arys["Properties"] =   [
            "NAME:Properties",
            "Enable:="        , "true"
        ]
    
'''

import re
from copy import deepcopy
from .complexDict import ComplexDict
from .common import log

def getArrayData(datas, keys):
    '''
    data is hfss array data
    keys is list or tuple 
    '''
    if len(keys) == 0:
        return None

    if len(keys)>1:
        keys1 = [keys[0]]
        keys2 = keys[1:]
        datas2 = getArrayData(datas,keys1)
        return getArrayData(datas2,keys2)
    
    else: #len(keys) == 1 
        
        for i in range(len(datas)):
            val = datas[i]
            
            if isinstance(val, (list,tuple)):
                key = "NAME:%s"%keys[0]
                for val2 in val:
                    if isinstance(val2, str) and key.lower() == val2.lower():
                        return val
            elif isinstance(val, (str)):
                key = "%s:="% keys[0]
                if key.lower() == val.lower():
                    return datas[i+1]
            else:
                continue
            
        raise Exception("key not in array:%s"%str(keys))
                    
def setArrayData(datas,keys,value):

    '''
    data is hfss array data
    keys is list or tuple 
    value is any type
    '''
    if len(keys) == 0:
        return None

    if len(keys)>1:
        keys1 = keys[:-1]
        keys2 = [keys[-1]]
        datas2 = getArrayData(datas,keys1)
        return setArrayData(datas2,keys2,value)
    
    else: #len(keys) == 1 
        flag = False
        for i in range(len(datas)):
            val = datas[i]
            if isinstance(val, (list,tuple)):
                key = "NAME:%s"%keys[0]
                for val2 in val:
                    if isinstance(val2, str) and key.lower() == val2.lower():
                        datas[i] = value
                        flag = True
            elif isinstance(val, (str)):
                key = "%s:="% keys[0]
                if key.lower() == val.lower():
                    datas[i+1] = value
                    flag = True
            else:
                continue
        
        if not flag:
            raise Exception("key error.%s"%str(keys))

def delArrayKey(datas,keys,ignorCase = True):
    if len(keys) == 0:
        return None

    if len(keys)>1:
        keys1 = [keys[0]]
        keys2 = keys[1:]
        datas2 = getArrayData(datas,keys1)
        return delArrayKey(datas2,keys2)
    
    else: #len(keys) == 1 
        
        for i in range(len(datas)):
            val = datas[i]
            
            if isinstance(val, (list,tuple)):
                key = "NAME:%s"%keys[0]
                for val2 in val:
                    if isinstance(val2, str) and key.lower() == val2.lower():
                        return datas.pop(i)
            elif isinstance(val, (str)):
                key = "%s:="% keys[0]
                if key.lower() == val.lower():
                    datas.pop(i)
                    return datas.pop(i)
            else:
                continue
            
        raise Exception("key not in array:%s"%str(keys))

class ArrayStruct(object):
    '''
    classdocs
    '''

    def __init__(self, datas = [], maps = None):
        '''
        Constructor
        '''
        self._datas = datas #tuple2list(datas) will change list id
        self.maps = maps
        self._keys = None
    
    def __del__(self):
        del self._datas
        
    def __getitem__(self, key):
        
        if isinstance(key, int):
            if len(self.Keys):
                #use for loop iteration
                return self.Keys[key]
            else:
                #use as list
                return self.Array[key]
        

        #map key have high priority then Array key
        if self.maps and isinstance(self.maps, dict):
            maps = ComplexDict(self.maps)
            if key in maps:
                log.debug("found key in array, mapKey: %s->%s:"%(key,maps[key]))
                mapKey = maps[key]
                if isinstance(mapKey,ComplexDict): #if map key is dict, execulte lambda function
                    if isinstance(mapKey["Key"], str): #if only one key
                        data = self.get(mapKey["Key"])
                        return mapKey["Get"](data)
                    elif isinstance(mapKey["Key"], (list,tuple)): #if more then one key
                        datas = [self.get(value) for value in mapKey["Key"]] 
                        return mapKey["Get"](*datas)
                    else:
                        pass
                else:
                    return self.get(mapKey)
        
        #Array key
        val = self.get(key)
        if isinstance(val, (list,tuple)):
            return self.__class__(val)
        else:
            return val
        #return self.get(key)
    
    def __setitem__(self,key,value):
        
        #map key have high priority then Array key
        if self.maps and isinstance(self.maps, dict):
            maps = ComplexDict(self.maps)
            if key in maps:
                log.debug("found key in array, mapKey: %s->%s:"%(key,maps[key]))
                mapKey = maps[key]
                if isinstance(mapKey,ComplexDict): #if map key is dict, execulte lambda function
                    if isinstance(mapKey["Key"], str): #if only one key
                        self.set(mapKey["Key"],mapKey["Set"](value))
                    elif isinstance(mapKey["Key"], (list,tuple)): #if more then one key, lambda should return same size value
                        for i in range(len(mapKey["Key"])):
                            self.set(mapKey["Key"][i],mapKey["Set"](value)[i])
                    else:
                        pass
                else:
                    self.set(mapKey,value)
                
                return None
        else:
            pass

        #Array key have lower priority
        self.set(key,value)
        
    def __delitem__(self,key):

        #map key have high priority then Array key
        if self.maps and isinstance(self.maps, dict):
            maps = ComplexDict(self.maps)
            if key in maps:
                log.debug("found key in array, mapKey: %s:"% key)
                mapKey = maps[key]
                if isinstance(mapKey,ComplexDict):
                    log.debug("Could not remove function maps keys: %s"%key)
#                     if isinstance(mapKey["Key"], str):
#                         self.set(mapKey["Key"],mapKey["Set"](value))
#                     elif isinstance(mapKey["Key"], (list,tuple)):
#                         for i in range(len(mapKey["Key"])):
#                             self.set(mapKey["Key"][i],mapKey["Set"](value)[i])
#                     else:
#                         pass
                else:
                    self.delKey(mapKey)
                
                return None
        else:
            pass

        #Array key have lower priority
        self.delKey(key)
        
    def __contains__(self,key):
        
        if self.maps and key in self.maps:
            return True
        
        if key in self.Keys:
            return True
        
        try:
            self[key]
            return True
        except:
            return False
        
        log.exception("Contains Error with key: %s"%key)
        
#         try:
#             self[key]
#         except:
#             return False
#         
#         return True
            
    def __getattr__(self,key):
        try:
            return  object.__getattribute__(self,key)
        except:
            log.debug("__getattribute__ from _options")
            return self[key] #self.get(key)

        raise Exception("Key not found: %s"%key)

         
    def __setattr__(self, key, value):
        if key in ["_datas","_keys","maps"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value
            
    def __dir__(self):
        return dir(self.__class__) + list(self.__dict__.keys()) + self.Keys
        
    def __len__(self):
        return len(self.Array)
        
    def __str__(self, *args, **kwargs):
        return str(self.Array)
        
    def __repr__(self, *args, **kwargs):
        return "ArrayStruct object:" + str(self.Array)

        
        
    @property
    def Keys(self):
        '''
        Returns:
            dict: the options in dict format
        '''
        
        if not self._keys:
            self._keys = []
            for item in self._datas:
                if isinstance(item, str) and item.endswith(":="):
                    self._keys.append(item[:-2] )
                if isinstance(item, (list,tuple)):
                    for subItem in item:
                        if isinstance(item, str) and item.startswith("NAME:"):
                            self._keys.append(subItem[5:])
        return self._keys
        
    @property
    def Array(self):
        return self._datas 
    
    @property
    def Datas(self):
        return self._datas 
    
    
    @Datas.setter
    def Datas(self):
        return self._datas 

    
    def get(self,path):
        '''
        return list data
        '''
        datas = self._datas
        if not path:
            return datas
        
        if isinstance(path, str):
            keyList = re.split(r"[\\/]", path)
            return self.get(keyList)
        
        if isinstance(path,(list,tuple)):
            keys = list(filter(lambda k:k.strip(),path)) #filter empty key
            return getArrayData(datas, keys)
        
        raise Exception("key not found: %s"%str(path))
        
    def set(self,path,value):
        datas = self._datas
        if not path:
            raise Exception("set key must give.")
        
        if isinstance(path, str):
            keyList = re.split(r"[\\/]", path)
            return self.set(keyList,value)
        
        if isinstance(path,(list,tuple)):
            keys = list(filter(lambda k:k.strip(),path)) #filter empty key
            return setArrayData(datas, keys, value)
        
        raise Exception("key not found: %s"%str(path))
    
    def append(self,key,value):
        val = list(self[key])
        val.append(value)
        self[key] = val
    
    def delKey(self,path):
        
        datas = self._datas
        if not path:
            raise Exception("set key must give.")
        
        if isinstance(path, str):
            keyList = re.split(r"[\\/]", path)
            return self.delKey(keyList)
        
        if isinstance(path,(list,tuple)):
            keys = list(filter(lambda k:k.strip(),path)) #filter empty key
            return delArrayKey(datas, keys)
            
        raise Exception("key not found: %s"%str(path))
        
        
    
    def update(self,datas):
        '''
        data should be like dict: dict, ComplexDict, ArrayStruct
        '''
        for item in datas:
            if item in self:
                self[item] = datas[item]
            else:
                log.debug("item not found when update ArrayStruct: %s"%item)
    
    def setMaps(self,maps):
        self.maps = maps
    
    def copy(self):
        return self.__class__(deepcopy(self.Array),maps = self.maps)