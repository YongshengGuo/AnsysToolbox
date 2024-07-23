#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230828


'''
used to get padstak information

'''

from .definition import Definitions,Definition


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
        