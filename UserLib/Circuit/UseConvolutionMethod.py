'''
Created on Mar 4, 2022

@author: yguo
'''

import sys
sys.path.append(r"C:\work\Study\Script\repository\win32API\AedtToolbox\magicBall\magicBall\bin\Release\SysLib")
from ActiveDesktop import getActiveDesktop,release
oDesktop = getActiveDesktop()

def array2List(ary):
    return [ary[i] for i in range(ary.Length)]
    

class circuitBase(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self.oDesktop = oDesktop
        self.oProject = oDesktop.GetActiveProject()
        self.oDesign = self.oProject.GetActiveDesign()
        self.oEditor = self.oDesign.SetActiveEditor("SchematicEditor") 

        
    
    def getSetups(self):
        oModule = self.oDesign.GetModule("SimSetup")
        return oModule.GetAllSolutionSetups()

    def getSetupData(self,setup):
        oModule = self.oDesign.GetModule("SimSetup")
        return oModule.GetSetupData(setup)
    
    def changeSetupValue(self,data,prop,value):
        data[data.index(prop)+1] = value
        
    def getSetupValue(self,data,prop):
        if prop in data:
            return data[data.index(prop)+1]
        else:
            return None
    
    def editSetupData(self,setup,prop,value):
        oModule = self.oDesign.GetModule("SimSetup")
        setupData = array2List(oModule.GetSetupData(setup))
        if not setupData:
            self.message("not found setup: %s"%setup)
            return
        name = self.getSetupValue(setupData, "Name:=")
        
        typ = None
        #modify
        if self.getSetupValue(setupData, "TransientData:="):
            typ = "Transient"
        elif self.getSetupValue(setupData, "LinearFrequencyData:="):
            typ = "LinearNetworkAnalysis"
        elif self.getSetupValue(setupData, "VerifEyeAnalysis:="):
            typ = "VerifEyeAnalysis"
        elif self.getSetupValue(setupData, "QuickEyeAnalysis:="):
            typ = "QuickEyeAnalysis"     
        elif self.getSetupValue(setupData, "AMIAnalysis:="):
            typ = "AMIAnalysis"
        else:
            self.message("Skip change the setup: %s  %s  %s"%(setup,prop,value))
            return
            
        self.changeSetupValue(setupData,prop,value)
        func = None
        exec("func = oModule.Edit"+typ)
        func(name,setupData)
        
    def message(self,msg,level = 0):
        debug = 3
        if level>debug:
            return
        print(msg)       
        if self.oDesktop: 
            self.oDesktop.AddMessage("","",0,msg)
        

def main():
    cir = circuitBase()
    setups = cir.getSetups()
    for setup in setups:
        cir.message("use Convolution method on setup:%s"%setup)
        cir.editSetupData(setup,"AdditionalOptions:=","s_element.convolution = 1")
    release()
    
if __name__ == "__main__":
    main()
