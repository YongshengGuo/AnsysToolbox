#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20240828

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
    layout = Layout()
    layout.initDesign()
    compOrder=[]
    netOrder=[]
    portOrder = []
    layout.Ports.reorder(compOrder,netOrder,portOrder)

#     layout.close()
    

    

if __name__ == '__main__':
#     test1()
    main()



