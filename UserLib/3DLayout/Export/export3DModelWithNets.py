#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com
#--- @Time: 2024-07-27


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

def export2HFSS():
    layout = Layout()
    layout.initDesign()
    if len(layout.Setups)<1:
        layout.Setups.add("HFSS")
    layout.Setups[0].exportToHfss()
    print("finished!")
    
def export2Q3D():
    layout = Layout()
    layout.initDesign()
    if len(layout.Setups)<1:
        layout.Setups.add("HFSS")
    layout.Setups[0].exportToQ3D()
    print("finished!")
    
def export2Maxwell():
    layout = Layout()
    layout.initDesign()
    if len(layout.Setups)<1:
        layout.Setups.add("HFSS")
    layout.Setups[0].exportToMaxwell()
    print("finished!")
    

if __name__ == '__main__':
#     test1()
    export2Maxwell()