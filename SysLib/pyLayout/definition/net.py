#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410



'''Net Object quick access

Examples:
    Get Net using full Net Name
    
    >>> Net["DQ0"]
    Net object
    
    Get Net using regular
    
    >>> Net["DQ\d+"]
    Net object list

    
    Get Net using regular
    
    >>> Net["DQ\d+"]
    Net object list
    
    Get Net using bus
    
    >>> Net["DQ[7:0]"]
    Net object list
    
    Get Net using bus and regular
    
    >>> Net["CH\d+_DQ[7:0]"]
    Net object list
    
'''


import re
from ..common.common import log
from ..common.unit import Unit
from ..common.complexDict import ComplexDict
from ..common.arrayStruct import ArrayStruct
from .definition import Definitions,Definition

class Net(Definition):
    '''_summary_
    '''
    maps = {}
    def __init__(self, name = None,layout = None):
        super(self.__class__,self).__init__(name,type="Net",layout=layout)
    
    @property
    def IsPowerNet(self):
        if self.name in self.layout.nets.PowerNetNames:
            return True
        else:
            return False
    
    @property
    def IsNaming(self):
        return not re.match(r"(^N[^a-z]+)|(^UNNAMED.*)$",self.name,re.I)
    
    
    def parse(self,force = False):
        '''
        mapping key must not have same value with maped key.
        '''
        
        if self.parsed and not force:
            return
        maps = self.maps.copy()
        _array = ArrayStruct([])
        self._info.update("Name",self.name)
        self._info.update("Array", _array)
        
        maps.update({"Objects":{
            "Key":"self",
            "Get":lambda s:s._getObjects()
            }})
            
        self._info.setMaps(maps)
        self._info.update("self", self)
        self.parsed = True
    
    def _getObjects(self):
        objectCDicts = ComplexDict()
        maps = {}
        objectCDicts.update("Net", self.name)
        for type in self.layout.primitiveTypes:
            objectCDicts.update(type+"s",type)
            fxDict = {
                "Key":("self",type+"s"),
                "Get":lambda s,k:s.getConnectedObjs(k)
                }
            maps.update({type+"s":fxDict})
        
        objectCDicts.update("All","*")
        maps.update({"All":{
            "Key":("self",type+"s"),
            "Get":lambda s,k:s.getConnectedObjs(k)
            }})
        objectCDicts.setMaps(maps)
        return objectCDicts
    

    def getConnectedPins(self):
        return self.getConnectedObjs('pin')

    
    def getConnectedComponnets(self):
        return self.getConnectedObjs('component')

    
    def getConnectedPorts(self):
        return self.getConnectedObjs('Port')

    
    def getConnectedObjs(self,typ = "*"):
        return self.layout.getObjectsbyNet(self.Name,typ)
    
    def getLength(self,unit = None):
        '''
        powerNet: return None
        shape with no lines: return None
        have lines: return total length of lines
        unit: the unit of return value
        '''
        if self.IsPowerNet:
            return None
        
        lines = self.getConnectedObjs('line')
        if not lines:
            return None

        segLens = [Unit(self.layout.lines[o].TotalLength) for o in lines]
        if unit is None:
            return sum(segLens)
        else:
            return Unit(sum(segLens))[unit]

    def createPortOnNet(self,comps = None,ignorRLC = True):

        if comps is None:
            compNames = self.getConnectedComponnets()
            if ignorRLC:
                compNames = [c for c in compNames if self.layout.Components[c].Type not in ["Resistor","Inductor","Capacitor"]]
         
        elif isinstance(comps, str):
            compNames = [comps]
         
        else:
            #comps is list 
            compNames= list(comps)

        self.layout.oEditor.CreatePortsOnComponentsByNet(
            ["NAME:Components"]+compNames,["NAME:Nets",self.Name], "Port", "0", "0", "0")

    def backdrill(self,stub=None):
        
        if self.IsPowerNet:
            log.info("Skip Backdrill on power/GND net : %s"%self.name)
            return
            
        log.info("Backdrill net : %s"%self.name)
        viaNames = self.getConnectedObjs("via")
        for via in viaNames:
            self.layout.vias[via].backdrill(stub = stub)
            
    def rename(self,newNet):
        objs = self.layout.oEditor.FindObjects('Net', self.Name)

        if len(objs)==0:
            log.info("not found objects on net %s"%self.Name)
            return
        
        self.layout.oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    [
                        "NAME:PropServers"
                    ] + list(objs),
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Net",
                            "Value:="        , newNet
                        ]
                    ]
                ]
            ])
    
    
    def delete(self):
        self.layout.oEditor.DeleteNets([self.Name])

class Nets(Definitions):

    def __init__(self,layout=None):
        super(self.__class__,self).__init__(layout, type="Net",definitionCalss=Net)

#     def _getDefinitionDict(self):
#         return  ComplexDict(dict([(name,Net(name,self.layout)) for name in self.layout.oEditor.GetNetClassNets('<All>')]))

    @property
    def DefinitionDict(self):
        if self._definitionDict == None:
            self._definitionDict  = ComplexDict(dict([(name,Net(name,self.layout)) for name in self.layout.oEditor.GetNetClassNets('<All>')]))
#             self._definitionDict  = self._getDefinitionDict()
        return self._definitionDict


    @property
    def SignalNetNames(self):
        allNets = self.layout.oEditor.GetNetClassNets('<All>')
        pwrNets = self.layout.oEditor.GetNetClassNets('<Power/Ground>')
        sigNets = [net for net in allNets if net not in pwrNets]
        sigNets.remove("<NO-NET>")
        return sigNets
        
    @property
    def PowerNetNames(self):
        return self.layout.oEditor.GetNetClassNets('<Power/Ground>') 
            
    #--- for Nets
    
    def getComponentsOnNets(self,nets,ignorRLC = True):
        
        if isinstance(nets, str):
            nets = [nets]
        
        temp = []
        for net in nets:
#             compNames = self.__class__(net).CompNames
            compNames = self.DefinitionDict[net].getConnectedComponnets()
            if ignorRLC:
                compNames = [c for c in compNames if self.layout.Components[c].PartType not in ["Resistor","Inductor","Capacitor"]]
            temp += compNames
            
        return list(set(temp))
    
    def createPortsOnNets(self,nets,comps = None,ignorRLC = True):

        if isinstance(nets, str):
            nets = [nets]
         
        if comps is None:
            compNames = self.getComponentsOnNets(nets,ignorRLC)
         
        elif isinstance(comps, str):
            compNames = [comps]
         
        else:
            compNames= comps
             
        self.layout.oEditor.CreatePortsOnComponentsByNet(
            ["NAME:Components"]+compNames,["NAME:Nets"]+nets, "Port", "0", "0", "0")

    def getRegularNets(self,regNets):
        '''_summary_

        Args:
            regNets (str,list): regular net. if space in regNets, will split to list.
            Signals: 需要保留的Signals, 支持多个信号，例如：“net1 net2”中间空格隔开，支持正则表达试，支持[7:0]总线写法”


        Returns:
            list: netNames list of regular input
        '''
        
        if type(regNets) == str:
#             regNets = [regNets]
            regNets = regNets.strip().split()
            
        #[7:0]
        nets = []
        for regNet in regNets:
            #support vector [15:0]
            rm = re.match(r".*\[(\d+):(\d+)\].*",regNet,re.IGNORECASE)
            if rm:
                H,L = [int(i) for i in rm.groups()[:2]]
                nets += [re.sub(r"\[(\d+:\d+)\]",str(i),regNet) for i in range(L,H+1)]
            else:
                nets.append(regNet)
                     
        regNets = nets #if len(nets)>0 else regNets
        
        
        nets = []

        for regNet in regNets:
            regNet = regNet.replace("$","\$").strip()
            nets += filter(lambda x: re.match(regNet+"$",x,re.IGNORECASE),self.NameList)
        return nets
    
    
    def deleteNets(self,netList):
        if not isinstance(netList, (list,tuple)) or len(netList)<1:
            log.info("deleteNets input is empty")
            return 
        
        self.layout.oEditor.DeleteNets(netList)
        
        
    def autoRLCnet(self,on = "C"):
        for each in on:
            if "r" == each.lower():
                reg = "R.*"
                tail = "_R"
            elif "l" == each.lower():
                reg = "L.*"
                tail = "_L"
            elif "c" == each.lower():
                reg = "C.*"
                tail = "_C"
            else:
                continue
            
            comps = self.layout.Components[reg]
            
            
            pwrNets = self.PowerNetNames
            i = 0
            for comp in comps:
#                 print("Process component: %s"%comp.Name)
                i += 1
                if len(comp.Pins) != 2:
                    continue
                
                pnet,nnet = comp.NetNames
    
                if pnet in pwrNets or nnet in pwrNets: 
                    log.debug("Component: %s, Pnet: %s, Nnet: %s %s"%(comp.Name,pnet,nnet,"................%s/%s"%(i,len(comps))))
                    continue
                
                log.debug("Component: %s, Pnet: %s, Nnet: %s %s"%(comp.Name,pnet,nnet,"................%s/%s"%(i,len(comps))))
                
                if re.match(r"^(N?\d+$)|(UNNAMED.*)|(\$.*)",pnet,re.I) and re.match(r"^N?[a-z0-9_]+[a-z]+",nnet,re.I): 
                    log.info(comp.Name+" Nets: "+ nnet + " " + pnet+ ": Rename "+ pnet + " to " + nnet+tail)
                    self.layout.Nets[pnet].rename(nnet+tail)
                if re.match(r"^(N?\d+$)|(UNNAMED.*)|(\$.*)",nnet,re.I) and re.match(r"^N?[a-z0-9_]+[a-z]+",pnet,re.I): 
                    log.info(comp.Name+" Nets: "+ pnet + " " + nnet + ": Rename "+ nnet + " to " + pnet+tail)
                    self.layout.Nets[nnet].rename(pnet+tail)