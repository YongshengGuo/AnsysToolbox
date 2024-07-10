#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20240420


import os
import re
import csv
import clr

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
        
from pyLayout import Layout,loadCSV,log
# pyLayout.log.setLogLevel(logLevel="DEBUG")



def main():

    layout = Layout("2023.2")
#     layout = Layout()
    layout.initDesign()

    layout.message("delete invalid RLC")
    layout.Components.deleteInvalidRLC()
    log.info("finished.")
        
if __name__ == '__main__':
#     test1()
    main()
    print("finished!")



    