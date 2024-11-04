#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410
'''
提供一种简单快捷的方式获取JSON 或者 dict的键值

Provide a simple way to access JSON cotent or dict variables

Examples:
    >>> ops = ComplexDict({
    "Header":
            {
                "Comment": "a demo"
            },
    "TempList": [1,2,3],
    "X":1,
    "Y",1
        })
    
    Access value using path mode for dict value
    >>> ops["/Header/Comment"]
    a demo
    >>> ops["Header/Comment"]  #first / is optional
    a demo
    
    Access using key list mode
    >>> ops[("Header","Comment")]
    
    assign values using path mode
    >>> ops["/Header/Comment"] = "demo2"
    
    assign values using key list mode
    >>> ops[("Header","Comment"] = "demo2"
    
    Test value in ComplexDict object
    >>> "/Header/Comment" in ops
    True
    
    maps: used to map alias key
    
    maps 用于使用别名映射ComplexDict现有的key，使用seMaps为ComplexDict设置maps映射
    如下，用X1映射ops中的X, Y1映射OPS中的Y
    >>> maps = {"X1":"X"，"Y1":Y}
    >>> ops.setMaps(maps)
    >>> ops.X1
    返回 OPS.X的值
    >>> ops.Y1
    返回 OPS.Y的值
    
    可以进行映射运算，改变数值，需要借助lambda表达式
    >>>> maps = {"X1":{key:X,"Get"：lambda x: x-1}}
    >>> ops.setMaps(maps)
    >>> ops.X1
    返回 ops.X -1 
    
    >>>> maps = {"X1":{key:X,"Set"：lambda x: x-1}}
    >>> ops.setMaps(maps)
    >>> ops.X1 = 2
    赋值 ops.X = 2-1
    
    多个运算值的支持，支持映射多个key并对起value进行运算，进行返回。 支持对数值运算后对多个key进行赋值操作。
    >>>> maps = {"X1":{key:(X,Y)},"Get"：lambda (x,y): x+y,"Set": lambda (x,y):(x+y,x-y)}
    >>> ops.setMaps(maps)
    >>> ops.X1
    返回 ops.X + ops.Y
    >>> ops.X1 = (2,5)
    赋值 ops.X = 2 + 5, ops.Y = 2 - 5

不要尝试图使用Get/Set函数Map已经存在的属性
    
Return:
    if return value is dict, will be return ComplexDict object, else return the value

'''
import sys
import os
import re
from copy import deepcopy
from .common import loadJson,writeJson,findDictValue,findDictKey,update2Dict,regAnyMatch
from .common import log

def getDictData(key, dict1, default = None,ignorCase = True):
        '''
        Args:
            key (str,list,tuple): the key paths, like "/Header/Comment"  or ("Header","Comment")
            dict1(dict1): dict to find
        return:
            value (any): value for the key
        '''

        if isinstance(dict1, (list,tuple)):
            return dict1[int(key)]
    
        if isinstance(key, str):
            # if key in dict1, return. even the key have "\/" char.
            val = findDictValue(key,dict1,default = "//key_not_found//", ignorCase = ignorCase)
            if val != "//key_not_found//":
                return val
            
            keyList = re.split(r"[\\/]", key,maxsplit = 1)
            keyList = list(filter(lambda k:k.strip(),keyList)) #filter empty key
            if len(keyList)<2:
                if default != None:
                    return default
                raise KeyError("key error: %s"%str(key))
            else:       
                return getDictData(keyList,dict1,default)
        
        if isinstance(key,(list,tuple)):
            key2 = list(filter(lambda k:k.strip(),key)) #filter empty key
            
            if len(key2) ==0:
                raise KeyError("emptey key:%s"%str(key))
            elif len(key2) ==1:
                return getDictData(key2[0],dict1,default)
            elif len(key2) ==2:
                dict2 = getDictData(key2[0],dict1,default)
                return getDictData(key2[1],dict2,default)

            else: # len(key2)>1:
                temp = dict1
                for k in key2:
                    if isinstance(temp, (list,tuple)):
                        temp =  temp[int(k)]
                    else:
                        temp = findDictValue(k, temp,default = default, ignorCase = ignorCase)
                
                val =  temp
            
            return val
        
        raise KeyError("key error: %s"%str(key))

def setDictData(key,value,dict1, ignorCase = True, enableUpdate = False):
    '''
    Args:
        key (str,list,tuple): the key paths, like "/Header/Comment"  or ("Header","Comment")
        value (any): value for the key
        dict1(dict): dict to set value
    '''
    if isinstance(dict1, (list,tuple)):
        dict1[int(key)] = value
        return
    
    if isinstance(key,str):
        k = findDictKey(key, dict1, ignorCase = ignorCase)
        if k!= "//key_not_found//":
            dict1[k] = value
            return
        
        if not re.findall(r"[\\/]",key):
            if enableUpdate:
                dict1[key] = value
            else:
                raise Exception("key error: %s"%str(key))
            
        keyList = list(filter(lambda k:k.strip(),re.split(r"[\\/]", key,maxsplit = 1)))
        return setDictData(keyList,value,dict1)
    
    elif isinstance(key,(list,tuple)): #value must dict or will be overrided
        key2 = list(filter(lambda k:k.strip(),key)) #filter empty key
        if len(key2) == 1: 
            return setDictData(key[0],value,dict1)

        elif len(key2) == 2: 
            dict2 = getDictData(key2[0],dict1)
            return setDictData(key2[1],value,dict2)

        else:
            key1 = key2[:-1]
            key2 =  key2[-1]
#                 temp = self[key1]
            temp = getDictData(key1,dict1,default = "//key_not_found//")
            if temp ==  "//key_not_found//":
                if enableUpdate:
                    temp[key] = value
                else:
                    raise Exception("key error: %s"%str(key))
            if isinstance(temp, (list,tuple)):
                temp[int(key2)] = value
            else:
                #option or dict
                temp[key2] = value

    else:
        raise Exception("key error: %s"%str(key))

def delDictKey(key,dict1,ignorCase = True):
    
    if isinstance(dict1, (list,tuple)):
        del dict1[int(key)]
        return
    
    if isinstance(key,str):
        k = findDictKey(key, dict1, ignorCase = ignorCase)
        if k!= "//key_not_found//":
            del dict1[k]
            return
        
        if not re.findall(r"[\\/]",key):
            raise Exception("key error: %s"%str(key))
            
        keyList = list(filter(lambda k:k.strip(),re.split(r"[\\/]", key,maxsplit = 1)))
        return delDictKey(keyList,dict1)
    
    elif isinstance(key,(list,tuple)): #value must dict or will be overrided
        key2 = list(filter(lambda k:k.strip(),key)) #filter empty key
        if len(key2) == 1: 
            return delDictKey(key[0],dict1)

        elif len(key2) == 2: 
            dict2 = getDictData(key2[0],dict1)
            return delDictKey(key2[1],dict2)

        else:
            key1 = key2[:-1]
            key2 =  key2[-1]
#                 temp = self[key1]
            temp = getDictData(key1,dict1,default = "//key_not_found//")
            if temp ==  "//key_not_found//":
                raise Exception("key error: %s"%str(key))
            if isinstance(temp, (list,tuple)):
                del temp[int(key2)]
            else:
                #option or dict
                del temp[key2]

    else:
        raise Exception("key error: %s"%str(key))
    

class ComplexDict(object): 

    '''
    Args:
        options(dict): options in dict format
        path(str): json path
        
        maps: { Key:{"Value":(x1,x2) ,"Get":lambda (x1,x2):xx*2, "Set":lambda x:xx=x}}
    '''

    def __init__(self,dictData=None, path = None, maps = None):
        self._dict = {}  #intial as empty dict
        self.ignorCase = True
        self.enableUpdate = False
        self.maps = maps
        if path:
            if os.path.exists(path):
                self._dict = loadJson(path)
            else:
                raise Exception("dictData not found:%s"%path)
            
        if isinstance(dictData, dict):
            self._dict = dictData
            
        if isinstance(dictData, self.__class__):
            self._dict = dictData.Dict
        
    def __getitem__(self, key):
        """
        Args:
            key(str): Access using path mode "/Header/Comment"
            key(list,tuple): access using key list mode ("Header","Comment")
        Returns:
            (ComplexDict): return ComplexDict object if a dict
            (Any) : return value if not a dict
        
        """
        
        #use for loop iteration, return values
        if isinstance(key, int):
            if isinstance(self._dict , (list,tuple)):
                self._dict[key]
            else:
                #return keys
                return self._dict[list(self._dict.keys())[key]]
        
        if isinstance(key, slice):
            return [self[i] for i in range(len(self))[key]]
            
        val = self.get(key,default= "//key_not_found//")
        if val == "//key_not_found//":
            raise KeyError("key error: %s"%str(key))
        
        #if dict, return ComplexDict(), else value
        if isinstance(val, (dict)):
            return self.__class__(val)
        else:
            return val
        
    def __setitem__(self,key,value):
        '''
        Args:
            key (str,list,tuple): the key paths, like "/Header/Comment"  or ("Header","Comment")
            value (any): value for the key
        '''
        self.set(key,value)
    

    def __contains__(self,key):
        
        if self.maps and key in self.maps:
            return True
        
        if key in self._dict:
            return True
        
        try:
            self.get(key)
            return True
        except:
            return False
        
        log.exception("Contains Error with key: %s"%key)

        
    def __delitem__(self,key):
        self.delKey(key)
        
    def __getattr__(self,key):
        if key in ['__get__','__set__']:
            #just for debug run
            return None
        
        if key in ["_dict","maps","ignorCase","enableUpdate"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]
        
#         try:
#             return  object.__getattr__(self,key)
#         except:
#             log.debug("__getattribute__ from _dict: %s"%key)
#             return self[key] #self.get(key)

        raise Exception("Key not found: %s"%key)

         
    def __setattr__(self, key, value):
        if key in ["_dict","maps","ignorCase","enableUpdate"]:
            object.__setattr__(self,key,value)
        else:
            log.debug("__setattribute__ from _dict: %s"%key)
            self[key] = value
    
    def __len__(self):
        return len(self._dict)
    
    def __str__(self, *args, **kwargs):
        return str(self._dict)
        
    def __repr__(self, *args, **kwargs):
        if isinstance(self._dict,dict):
            return "ComplexDict (dict) object with length: %s"%str(self._dict)
        elif isinstance(self._dict, (list,tuple)):
            return "ComplexDict (list) object with length: %s"%str(self._dict)
        else:
            return object.__repr__(self, *args, **kwargs)
        
    def __bool__(self):
        return bool(len(self._dict))
#     
#     def __dir__(self):
#         return list(dir(self.__class__)) + list(self.__dict__.keys())  + list(self._dict.keys())
    
    
    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)

    @property
    def Props(self):
        propKeys = list(self._dict.keys())
        if self.maps:
            propKeys += list(self.maps.keys())
        
        return propKeys
    
    @property
    def Values(self):
        '''
        Returns:
            dict: the options in dict format
        '''
        return self._dict.values()
    
    @property
    def Keys(self):
        '''
        Returns:
            dict: the options in dict format
        '''
        return self._dict.keys()
    
    @property
    def Items(self):
        '''
        Returns:
            dict: the options in dict format
        '''
        return self._dict.items()
    
    @property
    def Count(self):
        '''
        Returns:
            dict: the options in dict format
        '''
        return len(self._dict)
    
    @property
    def Dict(self):
        '''
        Returns:
            dict: the options in dict format
        '''
        return self._dict
    
    def updates(self,dict2,copy=True):
        '''
        dict2 update to dict1, considered Multi-level dict keys, with deepcopy
        '''
        dict2 = ComplexDict(dict2) #map key should be consider
        
        copyMethod = deepcopy if copy else lambda x:x
        
        if not self.Dict:
            self._dict = copyMethod(dict2._dict)
        
        for key in dict2.Keys:
            try:
                val = self.get(key,default= "//key_not_found//") #val is dict or value
            except:
                log.warning("key:%s not found in layer: %s"%(key,self.Name))
                
            if val == "//key_not_found//": #not found
                if isinstance(dict2[key], (dict,ComplexDict)):
                    self.update(key, copyMethod(dict2._dict[key]))
                else:
                    self.update(key,dict2[key])
            else:
                if isinstance(val, (dict,ComplexDict)):
                    val2 = ComplexDict(val)
                    val2.updates(dict2[key])
                    self[key] = val2.Dict
                else:
#                     log.debug(key,dict2[key])
                    self[key] = dict2[key]
#                     self.update(key, dict2[key])
                    
    def update(self,key,value):
        self._dict[key] = value
        
    def append(self,dict2):
        self._dict.update(dict2._dict)
    
    def setMaps(self,maps):
        self.maps = maps
    
    
    def get(self,key,default = None):
        '''
        datas: {key1:value1}
        maps: {key2:key1}
        
        get(key2) from datas
        
        firt try to get from maps, then dict
        
        return dict or value
        
        fa = lambda (x,y):x+y
        fa([1,2])
        
        fb = lambda (a,b),(x,y):(a+b,x+y)
        fb([1,2],[3,4])
        
        '''
        #map key have high priority then Array key
        if self.maps and isinstance(self.maps, dict):
            maps = ComplexDict(self.maps)
            if key in maps:
                mapKey = maps[key]
                log.debug("found key in maps: %s->%s:"%(key,mapKey))
                if isinstance(mapKey,ComplexDict): #if map key is dict, execulte lambda function
                    if isinstance(mapKey["Key"], str): #if only one key
                        data = getDictData(mapKey["Key"],self._dict, default = "//key_not_found//") 
                        if data != "//key_not_found//":
                            return mapKey["Get"](data)
                        elif "Default" in mapKey:
                            return mapKey["Default"]
                        else:
                            raise KeyError("key error: %s"%str(mapKey))
                        
                    elif isinstance(mapKey["Key"], (list,tuple)): #if more then one key, lambda should return same size value
                        datas = [getDictData(value,self._dict, default = "//key_not_found//") for value in mapKey["Key"]] 
                        if not regAnyMatch("//key_not_found//", datas):
                            return mapKey["Get"](*datas)
                        elif "Default" in mapKey:
                            return mapKey["Default"]
                        else:
                            raise KeyError("key error: %s"%str(mapKey))
                    else:
                        pass
                else:
                    #return map key values
                    val = getDictData(mapKey,self._dict, default = "//key_not_found//")
                    if val != "//key_not_found//":
                        return val
        
        val = getDictData(key, self._dict, default = "//key_not_found//")
        
        if val == "//key_not_found//":
            if default == None:
                raise KeyError("key error: %s"%str(key))
            else:
                return default
        else:
            return val
    
    def set(self,key,value):
        '''
        set key to dict
        maps key have high priority then dict
        '''
        
        #map key have high priority then Array key
        if self.maps and isinstance(self.maps, dict):
            maps = ComplexDict(self.maps)
            if key in maps:
                log.debug("found key in array, mapKey: %s->%s:"%(key,maps[key]))
                mapKey = maps[key]
                if isinstance(mapKey,ComplexDict):
                    if isinstance(mapKey["Key"], str):
                        returnValue = mapKey["Set"](value)
                        if returnValue!=None: 
                            setDictData(mapKey["Key"],returnValue,self._dict)
                        else:
                            #if returnValue is none value, which mean returnValue not need,value is set by function.
                            pass
                        
                    elif isinstance(mapKey["Key"], (list,tuple)):
                        returnValue = mapKey["Set"](value)
                        for i in range(len(mapKey)):
                            if returnValue!=None: 
                                setDictData(mapKey["Key"][i],returnValue[i],self._dict)
                            else:
                                #if returnValue is none value, which mean returnValue not need,value is set by function.
                                pass
                    else:
                        pass
                else:
                    setDictData(mapKey,value,self._dict)
                
                return None
        else:
            pass
        
        setDictData(key,value,self._dict,enableUpdate=self.enableUpdate)
        
#         try:
#             setDictData(key,value,self._dict)
#             return
#         except:
#        
#         if self.enableUpdate:
#             setDictData(key,value,self._dict,enableUpdate=True)
# 
#         raise Exception("key error: %s"%str(key))
    
    
    def getMappingKeys(self,key):
        '''
        get dict really keys from maps key
        '''
        if not isinstance(key, str): #isinstance(k, str) add 20240428 yongsheng Guo
            return key
        
        
        if isinstance(self.maps, dict):
            for k,v in self.maps.items():
                if isinstance(k, str) and k.lower() == key.lower(): #isinstance(k, str) add 20240428 yongsheng Guo
                    log.debug("found key in maps, mapKey: %s:"% v)
                    return v["Key"] if isinstance(v, dict) else v
            
        return "//key_not_found//"
    
    def getReallyKey(self,key):
        '''
        get key from maps or dict
        '''
        if not isinstance(key, str): #isinstance(k, str) add 20240428 yongsheng Guo
            return key
        
        key2 = self.getMappingKeys(key)
        if key2 != "//key_not_found//":
            return key2
        else:
            for k in self._dict:
                if k.lower() == key.lower():
                    return k
            return key

    def delKey(self,key):
        
        if self.maps and isinstance(self.maps, dict):
            for k,v in self.maps.items():
                if k.lower() == key.lower():
#                     log.debug("found key in maps, mapKey: %s:"% v)
                    if isinstance(v, dict):
                        log.debug("Could not remove function maps keys: %s"%key)
                        return None
                    else:
                        log.debug("del key from map key %s:"% k)
                        delDictKey(v,self._dict)
                        return None
                        
        delDictKey(key,self._dict)
        
                    
    def copy(self):
        return self.__class__(deepcopy(self.Dict))
    
    
    def writeJosn(self,path):
        writeJson(path,self._dict)
    

    def loadConfig(self,config):
        
        if isinstance(config, str):
            #config path
            if os.path.exists(config):
                self._dict = loadJson(config)
            else:
                raise Exception("dictData not found:%s"%config)
  
        elif isinstance(config, dict):
            #dict options
            self._dict = config
            
        elif isinstance(config, ComplexDict):
            self._dict = config.Dict
        
        else:
            raise Exception("loadConfig: config must be path,dict or ComplexDict. %s"%str(config))
    
#     @classmethod
#     def load(cls,config):
#         if isinstance(config, str):
#             #config path
#             return cls(path = config)
#         elif isinstance(config, dict):
#             #dict options
#             return cls(dictData = config)
#              
#         elif isinstance(config, ComplexDict):
#             return config
#          
#         else:
#             raise Exception("loadConfig: config must be path,dict or ComplexDict. %s"%str(config))
