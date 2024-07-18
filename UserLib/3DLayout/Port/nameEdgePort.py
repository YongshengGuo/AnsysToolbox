#--- coding:utf-8
#--- @Author: yongsheng.guo@ansys.com
#--- @Time: 2023-07-02


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


def main():

    layout = Layout()
    # layout1.openAedt(r"C:\work\Project\AE\Script\packageOnPCB\PCB.aedt")
    layout.initDesign()
    
    for port in layout.Ports.All:
        #already is named port, skip
        if "." in port.Name:
            layout.log.info("skip port: %s"%port.Name)
            continue
            
        ConnectionPoints = port.ConnectionPoints #0.000400 0.073049 Dir:270.000000 Layer: BOTTOM    
        splits = ConnectionPoints.split() #['0.000400', '0.073049', 'Dir:270.000000', 'Layer:', 'BOTTOM']
        X = float(splits[0])
        Y = float(splits[1])
        layer = splits[-1]
        posObjs = list(layout.getObjectByPoint([X,Y],layer = layer,radius="2mil"))
        print(port.Name,posObjs,layer)

        if port.Name in posObjs:
            posObjs.remove(port.Name)
#             
#         posObj = posObjs[0]
        posObj = None
        for obj in posObjs:
            if obj in layout.Pins:
                posObj = obj
                break
        if not posObj:
            posObj = posObjs[0]
            
        if posObj in layout.Pins:   
            tempList = list(posObj.split("-"))+[layout.Pins[posObj].Net]
            newName = ".".join(tempList)
    #         print(newName,port)
            layout.log.info("Rename %s to %s"%(port.Name,newName))
            port.Port = newName
        else:
            newName = layout[posObj].Net
            layout.log.info("Rename %s to %s"%(port.Name,newName))
            port.Port = newName
        

    
if __name__ == '__main__':
#     test1()
    main()
    