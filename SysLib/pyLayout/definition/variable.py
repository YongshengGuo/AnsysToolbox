#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2023-04-09

'''
变量管理模块
Examples:
    Add variable to active design
    >>> varbs = Variable(layout=layout)
    >>> varbs.add("len","10in")
    >>> varbs["len"].Value
    10in
    
    chang varbs["len"] Value
    >>> varbs["len"] = "20in"
    >>> varbs["len"].Value
    20in
    
    varbs["len"] could be convert to str implicitly 
    >>> log.debug(varbs["len"])
    20in
    
    if variable start with $, will add as project variable
    >>> varbs.add("$len2","5in")
    >>> log.debug(varbs["len"])
    5in
    
Raises:
    key error: varbs["len2"]variable name not in Project or design
        
'''

import re
from ..common.complexDict import ComplexDict
from ..common.common import log

class Variable(object):
    '''_summary_
    '''
    layoutTemp = None
    def __init__(self,varName = None,layout=None):
        '''Initialize Component object
        Args:
            compName (str): refdes of component in PCB, optional
            layout (PyLayout): PyLayout object, optional
        '''
        self.name = varName
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
        else:
            self.layout = self.__class__.layoutTemp
            
            
    def __str__(self):
        return str(self.Value)

    def __repr__(self):
        return str(self.Value)
            
    @property
    def oProject(self):
        return self.layout.oProject
    
    @property
    def oDesign(self):
        return self.layout.oDesign
    
    @property
    def Value(self):
        return self.get()
    
    @Value.setter
    def Value(self,val):
        self.set(val)
    
    def set(self,val):    
        var = self.name
        obj = self.oProject if var.startswith("$") else self.oDesign
        obj.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:%s"%("ProjectVariableTab" if var.startswith("$") else "LocalVariableTab"),
                    [
                        "NAME:PropServers", 
                        "%s"%("ProjectVariables" if var.startswith("$") else "LocalVariables")
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:%s"%var,
                            "Value:=", "%s"%val
                        ]
                    ]
                ]
            ])
        
    def get(self):
        var = self.name
        obj = self.oProject if var.startswith("$") else self.oDesign
        val = obj.GetVariableValue(var)
        return val
    
        
        
class Variables(object):


    def __init__(self,layout=None):
        '''Initialize Variables object
        '''
        
        self.layout = layout
        self.variableDict = None

            
    def __getitem__(self, key):
        """
        key: str, regex, list, slice
        """
        
        if isinstance(key, int):
            return self.VariableDict[key]
        
        if isinstance(key, slice):
            return self.VariableDict[key]
        
        if isinstance(key, str):
            if key in self.VariableDict:
                return self.VariableDict[key]
            else:
                #find by 正则表达式
                lst = [name for name in self.VariableDict.Keys if re.match(r"^%s$"%key,name,re.I)]
                if not lst:
                    raise Exception("not found component: %s"%key)
                else:
                    #如果找到多个器件（正则表达式），返回列表
                    return self[lst]

        if isinstance(key, (list,tuple)):
            return [self[i] for i in list(key)]

            
    def __setitem__(self,key,value):
        '''
        Args:
            key (str,list,tuple): the key paths, like "/Header/Comment"  or ("Header","Comment")
            value (any): value for the key
        '''
        self.VariableDict[key].set(value)
#         Variable(key).set(value)
        
    def __contains__(self,key):
        return key in self.VariableDict

        
    def __getattr__(self,key):
        #当调用一个不存在的属性时，就会触发__getattr__()
 
        if key in ['__get__','__set__']:
            #just for debug run
            return None
         
        try:
            return object.__getattribute__(self,key)
        except:
            log.debug("Variables __getattribute__ from _info: %s"%str(key))
            return self[key]
         
#     def __getattr__(self,key):
#         try:
# #             return super(self.__class__,self).__getattr__(key)
#             log.debug(dir(object))
#             return object.__getattr__(self,key)
#         except:
#             log.debug("__getattribute__ from _info")
#             return self[key]
         
          
    def __setattr__(self, key, value):
        if key in ["layout","variableDict"]:
            object.__setattr__(self,key,value)
        else:
            self[key] = value
    
    def __len__(self):
        return len(self.VariableDict)
    
    @property
    def VariableDict(self):
        if self.variableDict is None:
            ProjectVars,designVars = self.layout.oProject.GetVariables(),self.layout.oDesign.GetVariables()
            self.variableDict  = ComplexDict(dict([(var,Variable(var,layout=self.layout)) for var in ProjectVars+designVars]))
            self.variableDict.setMaps(dict([(re.sub(r'[$]','_',var),var) for var in ProjectVars]))
        return self.variableDict
    
    @property
    def All(self):
        return self.VariableDict
    

    def add(self,var,val = 0):
        if var in self.layout.oProject.GetVariables() + self.layout.oDesign.GetVariables():
            log.debug("Return for variable exist: %s"%var)
            return
        
        obj = self.layout.oProject if var.startswith("$") else self.layout.oDesign
        obj.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:%s"%("ProjectVariableTab" if var.startswith("$") else "LocalVariableTab"),
                    [
                        "NAME:PropServers", 
                        "%s"%("ProjectVariables" if var.startswith("$") else "LocalVariables")
                    ],
                    [
                        "NAME:NewProps",
                        [
                            "NAME:%s"%var,
                            "PropType:=", "VariableProp",
                            "UserDef:=", True,
                            "Value:=", "%s"%val
                        ]
                    ]
                ]
            ])
        self.variableDict = None