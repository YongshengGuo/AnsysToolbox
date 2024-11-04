#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230828


'''
used to get padstak information

'''

import os,re
from .definition import Definitions,Definition
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common import hfss3DLParameters
from ..common.common import log,tuple2list

class ComponentDef(Definition):
    '''

    Args:
    '''
    
    def __init__(self, name = None,array = None,layout = None):
        super(self.__class__,self).__init__(name,type="Component",layout=layout)
    

    def rename(self,newName):
        self.Info.Array[0] = "NAME:%s"%newName
        self.update()
        self.layout.ComponentDefs.refresh()
        return
    
    

class ComponentDefs(Definitions):
    

    def __init__(self,layout=None):
        super(self.__class__,self).__init__(layout, type="Component",definitionCalss=ComponentDef)

    def add(self,name):
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oComponentManager = oDefinitionManager.GetManager("Component")
        oComponentManager.Add(["NAME:%s"%name])
        self.push(name)
        
#     def addSNPDef(self,path,name=None):
        #"CosimulatorType:=", 102 for spice model
    def addSNPDef(self,modelName):
#         if not name:
#             name = os.path.split(path)[-1] 
#         name = re.sub("[\.\s#]","_",name)
        
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oComponentManager = oDefinitionManager.GetManager("Component")
        
        ary = ArrayStruct(tuple2list(hfss3DLParameters.componentLib_snp)).copy()
        ary.Array[0] = "NAME:%s"%modelName
        ary.Info.DataSource = self.layout.ModelDefs[modelName].filename
        ary.ModelDefName = modelName
        ary.CosimDefinitions.CosimDefinition.CosimDefName = modelName
        ary.CosimDefinitions.CosimDefinition.ModelDefinitionName = modelName
        ary.CosimDefinitions.DefaultCosim = modelName
          
        if modelName in self.NameList:
            oComponentManager.Edit(modelName,ary.Array)
        else:
            oComponentManager.Add(ary.Array)
            self.push(modelName)

#         ary = ["NAME:%s"%modelName,["NAME:CosimDefinitions","ModelDefName:=", modelName,["NAME:CosimDefinition","CosimulatorType:=", 102,"CosimDefName:=", modelName,
#                  "IsDefinition:=", True,"Connect:=", True,"ModelDefinitionName:=", modelName],
#                 "DefaultCosim:=", "Default"]]
#  
#         if modelName in self.NameList:
#             oComponentManager.Edit(modelName,ary)
#         else:
#             oComponentManager.Add(ary)
#             self.push(modelName)
        
        self[modelName].parse()
        return self[modelName]
        
    def addSpiceDef(self,name):
        oDefinitionManager = self.layout.oProject.GetDefinitionManager()
        oComponentManager = oDefinitionManager.GetManager("Component")
        #"CosimulatorType:=", 112 for spice model
        
        ary = ["NAME:%s"%name,["NAME:CosimDefinitions",["NAME:CosimDefinition","CosimulatorType:=", 112,"CosimDefName:=", "Default",
                 "IsDefinition:=", True,"Connect:=", True,"ModelDefinitionName:=", name],
                "DefaultCosim:=", "Default"]]
        if name in self.NameList:
            oComponentManager.Edit(name,ary)

        else:
            oComponentManager.Add(ary)
            self.push(name)
        
        self[name].parse()
        return self[name]
            