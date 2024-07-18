#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20230611


import os
import re
import csv
import clr
clr.AddReference('System.Windows.Forms')

import sys,os
appPath = os.path.realpath(__file__)
appDir = os.path.split(appPath)[0] 
sys.path.append(appDir)
sys.path.append(r"C:\work\Study\Script\Ansys\quickAnalyze\FastSim")
# MessageBox.Show(appDir)
try:
    import pyLayout
except:
    import clr
    layoutlib = os.path.join(appDir,'pyLayout.dll')
    if os.path.exists(layoutlib):
        print("import pyLayout.dll")
        clr.AddReferenceToFileAndPath(layoutlib)
        import pyLayout
        
from pyLayout import Layout
# pyLayout.log.setLogLevel(logLevel="DEBUG")



def main():
    layout = Layout("2022.2")
#     layout = Layout()
    layout.initDesign()
    csvPath = os.path.join(layout.projectDir,layout.ProjectName+"_"+layout.DesignName + ".csv")
    layout.Layers.exportCsv(csvPath)
    os.system("start %s"%csvPath)

if __name__ == '__main__':
#     test1()
    main()