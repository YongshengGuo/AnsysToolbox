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
from .definition import Definitions,Definition
from ..common.arrayStruct import ArrayStruct

class Variable(Definition):
    '''_summary_
    '''
    layoutTemp = None
    def __init__(self,name = None,layout=None):
        '''Initialize Component object
        Args:
            compName (str): refdes of component in PCB, optional
            layout (PyLayout): PyLayout object, optional
        '''
        super(self.__class__,self).__init__(name,type="Variable",layout=layout)

            
            
    def __str__(self):
        return str(self.Value)

    def __repr__(self):
        return "Variable Object %s: %s"%(self.name,self.Value)
            

    def parse(self,force = False):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if self.parsed and not force:
            return
        maps = self.maps.copy()
        _array = ArrayStruct([])
        self._info.update("Name",self.name)
        self._info.update("Array", _array)

        maps.update({"Value":{
            "Key":"name",
            "Get":lambda k: self.get(),
            "Set":lambda k,v: self.set(v)
            }})
        
        self._info.setMaps(maps)

        self.parsed = True
    
    
#     @property
#     def Value(self):
#         return self.get()
#     
#     @Value.setter
#     def Value(self,val):
#         self.set(val)
    
    def set(self,val):    
        var = self.name
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
        obj = self.layout.oProject if var.startswith("$") else self.layout.oDesign
        val = obj.GetVariableValue(var)
        return val
    
        
        
class Variables(Definitions):


    def __init__(self,layout=None):
        '''Initialize Variables object
        '''
        super(self.__class__,self).__init__(layout, type="Variable",definitionCalss=Variable)


    def __setitem__(self, key, value):
        self[key].Value = value
        
    def  __setattr__(self, key, value):
        if key in ["layout","definitionCalss","type","_definitionDict"]:
            object.__setattr__(self,key,value)
        elif key in self.DefinitionDict:
            self[key].Value = value
        else:
            log.error("%s not a variable"%key)
            
    @property
    def DefinitionDict(self):
        if self._definitionDict is None:
            ProjectVars,designVars = self.layout.oProject.GetVariables(),self.layout.oDesign.GetVariables()
            self._definitionDict  = ComplexDict(dict([(var,Variable(var,layout=self.layout)) for var in ProjectVars+designVars]))
            self._definitionDict.setMaps(dict([(re.sub(r'[$]','_',var),var) for var in ProjectVars]))
        return self._definitionDict
    

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
        self._definitionDict = None