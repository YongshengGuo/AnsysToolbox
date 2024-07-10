#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2023-04-24

'''
Solution represents the smallest unit of results in a 3D layout, which can be understood as a collection of SNPs.
Solution代表3D Layout中结果的最小单元，可以理解为一个SNP的结集。


Examples:
    Add HFSS setupName
    >>>
    
'''
import os
import re
from ..common.complexDict import ComplexDict
from ..common.common import log

class Solution(object):
    
    layoutTemp = None
    
    def __init__(self,name = None,variation = None,layout=None):
        
        self.name = name
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
        else:
            self.layout = self.__class__.layoutTemp
        
#     @property
#     def oModule(self):
#         if not self._oModule:
#             self._oModule = self.oDesign.GetModule("SolveSetups")
#         return self._oModule
    
    @property
    def Name(self):
        return self.name
    
    
    def exportSNP(self,path = None):
        self.exportNetworkData(path)
        
    def exportNetworkData(self,path = None):
        solutionName = self.name
        ext = ".s%sp"%len(self.layout.Ports)
        
        if not path:
#             path = self.layout.projectDir + "\%s"%solutionName
            path = os.path.join(self.layout.projectDir,"_".join([self.layout.projectName,self.layout.designName])+ext)
        
        elif ext not in path:
            path += ext
        else:
            pass
        self.layout.oDesign.ExportNetworkData("", [solutionName], 3, path, ["ALL"], True, 50, "S", -1, 0, 15)
#         variation_array=self.oModule.ListVariations(solutionName)
#         self.oDesign.ExportNetworkData(variation_array[0], [solutionName], 3, path, ["ALL"], True, 50, "S", -1, 0, 15)
        
    
    
    
#     @classmethod
#     def getSolution(cls,setupName,sweepName):
#         return cls(setupName = setupName,sweepName = sweepName)
#     
#     @classmethod
#     def getAllSetupSolution(cls):
#         solutions = []
#         oModule = cls.layout.oDesign.GetModule("SolveSetups")
#         setups = oModule.GetSetups()
#         for setup in setups:
#             for sweep in oModule.GetSweeps(setup):
#                 solutions.append(cls.getSolution(setup, sweep))
#         
#         return solutions
#        
#     @classmethod
#     def getAllSolution(cls):
#         '''
#         Solutions include optimetrics, all exist in design
#         '''
#         pass


class Solutions(object):
    
    def __init__(self,layout=None):
        self.solutionDict = None #ComplexDict component buffer
        
        self.layout = layout
        if layout:
            Solution.layoutTemp = layout
            
    def __getitem__(self, key):
        """
        key: str, regex, list, slice
        """
        
        if isinstance(key, int):
            return self.SolutionDict[key]
        
        if isinstance(key, slice):
            return self.SolutionDict[key]
        
        if isinstance(key, str):
            if key in self.SolutionDict:
                return self.SolutionDict[key]
            else:
                #find by 正则表达式
                lst = [name for name in self.SolutionDict.Keys if re.match(r"^%s$"%key,name,re.I)]
                if not lst:
                    raise Exception("not found component: %s"%key)
                else:
                    #如果找到多个器件（正则表达式），返回列表
                    return self[lst]

        if isinstance(key, (list,tuple)):
            return [self[i] for i in list(key)]
    
    def __getattr__(self,key):
        if key in ['__get__','__set__']:
            #just for debug run
            return None
        
        try:
            return super(self.__class__,self).__getattribute__(key)
        except:
            log.debug("Lines __getattribute__ from _info: %s"%str(key))
            return self[key]
    
    def __contains__(self,key):
        return key in self.SolutionDict
    
    def __len__(self):
        return len(self.SolutionDict)
    
    @property
    def SolutionDict(self):
        if self.solutionDict is None:
            solutionDict = {}
            maps = {}
            oModule = self.layout.oDesign.GetModule("SolveSetups")
            setups = oModule.GetSetups()
            for setup in setups:
                for sweep in oModule.GetSweeps(setup):
                    name = "%s:%s"%(setup,sweep)
                    solutionDict.update({name:Solution(name,layout=self.layout)})
                    maps.update({"%s_%s"%(setup,sweep):"%s:%s"%(setup,sweep)})

            self.solutionDict  = ComplexDict(solutionDict,maps=maps)
        return self.solutionDict 
    
    @property
    def All(self):
        return self.SolutionDict
    
    def refresh(self):
        self.solutionDict = None