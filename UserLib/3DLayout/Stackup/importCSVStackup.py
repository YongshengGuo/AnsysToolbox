#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20230611


import os
import re
import csv
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import OpenFileDialog,SaveFileDialog,DialogResult,MessageBox

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

def openFile(fileFilter = "All files(*.*)|*.*", initialDirectory=None):
    fd = OpenFileDialog()
    fd.Filter = fileFilter 
    # fd.RestoreDirectory = True
    if initialDirectory:
        fd.InitialDirectory = initialDirectory
        
    if fd.ShowDialog() == DialogResult.OK:
        return str(fd.FileName)
    else:
        return ""

def main():
    # csvPath = openFile("(*.csv)|*.csv|All files(*.*)|*.*")
    # if not csvPath:
    #     return
    layout = Layout()
#     layout = Layout()
    layout.initDesign()
    
    csvPath = openFile("(*.csv)|*.csv|All files(*.*)|*.*",layout.projectDir)
    if not csvPath:
        return
    
    layout.Layers.loadFromCSV(csvPath)

if __name__ == '__main__':
#     test1()
    main()