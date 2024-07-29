#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2024-07-26

from .Aedt3DToolBase import Aedt3DToolBase

class Icepak(Aedt3DToolBase):

    def __init__(self, version=None, installDir=None,nonGraphical=False):
        super(self.__class__,self).__init__(toolType="Icepak",version=version, installDir=installDir,nonGraphical=nonGraphical)
    
    
#for test
if __name__ == '__main__':
#     layout = Layout("2022.2")
    layout = Icepak("2023.2")
    layout.initDesign()