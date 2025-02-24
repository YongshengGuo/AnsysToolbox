#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com
#--- @Time: 2024-11-13


maxDrill = "4.5mil"

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
from pyLayout import Unit
# pyLayout.log.setLogLevel(logLevel="DEBUG")

def main():
    layout = Layout()
    layout.initDesign()
    
    for via in layout.Vias.All:
        if Unit(via.HoleDiameter)<Unit(maxDrill):
            loc = via.Location
            startLayer = via.StartLayer
            stopLayer = via.StopLayer
            drawLayer = layout.Layers[startLayer].offLayer(1).Name
            r = Unit(via.HoleDiameter)/2 # + "2mil"
            while drawLayer != stopLayer:
#                 name = layout.Circles.getUniqueName("keepViaPad_%s_%s_"%(via.Name,drawLayer))
                name = "keepViaPad_%s_%s"%(via.Name,drawLayer)
                if name in layout.Circles:
                    layout.log.info("Via pad '%s' already exist, skip."%name)
                else:
                    layout.log.info("Keep pad for Via '%s' in layer '%s'"%(via.Name,drawLayer))
                    layout.CreateCircle(layer=drawLayer,location=loc,r=r,name=name)
                    layout.Circles[name].Net = via.Net
                    
                drawLayer = layout.Layers[drawLayer].offLayer(1).Name
            

if __name__ == '__main__':
#     test1()
    main()
    print("finished.")