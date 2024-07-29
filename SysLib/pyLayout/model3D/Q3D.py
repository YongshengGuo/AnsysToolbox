#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2024-07-26

from .Aedt3DToolBase import Aedt3DToolBase

class Q3D(Aedt3DToolBase):

    def __init__(self, version=None, installDir=None,nonGraphical=False):
        super(self.__class__,self).__init__(toolType="Q3D Extractor",version=version, installDir=installDir,nonGraphical=nonGraphical)
    
#for test
if __name__ == '__main__':
#     layout = Layout("2022.2")
    layout = Q3D()
    layout.initDesign()