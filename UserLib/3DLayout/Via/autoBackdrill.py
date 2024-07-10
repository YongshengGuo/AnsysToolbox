#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20231112

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

import sys,os,re
appPath = os.path.realpath(__file__)
appDir = os.path.split(appPath)[0] 
sys.path.append(appDir)
sys.path.append(r"C:\work\Study\Script\Ansys\quickAnalyze\FastSim")


from backdrillForm import Form1
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
    layout.initDesign()

    form = Form1()
    form.layout = layout
#     form.Show()
#     form.Activate()
#     form.ShowDialog()
    from System.Windows.Forms import Application
    Application.Run(form)
    form.Dispose()

if __name__ == '__main__':
#     test1()
    main()
