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
from  ..common.complexDict import ComplexDict


class Net(object):
    '''_summary_
    '''
    layoutTemp = None
    maps = {}
    objTypes = ['pin', 'via', 'rect', 'arc', 'line', 'poly', 'plg', 
                 'circle void', 'line void', 'rect void', 'poly void', 
                 'plg void', 'text', 'cell', 'Measurement', 'Port', 
                 'Port Instance', 'Port Instance Port', 'Edge Port', 
                 'component', 'CS', 'S3D', 'ViaGroup']
    def __init__(self,netName = None,layout=None):
        '''Initialize Component object
        Args:
            compName (str): refdes of component in PCB, optional
            layout (PyLayout): PyLayout object, optional
        '''
        
        self.name = netName
        self.parsed = None
        self._info = None
        if layout:
            self.__class__.layoutTemp = layout
            self.layout = layout
        else:
            self.layout = self.__class__.layoutTemp

    def __repr__(self):
        return "Net Object: %s"%self.Name

    def __getitem__(self, key):
        """
        key: str
        """
        self.parse()
        if key in self._info: 
            key1 = self._info.getReallyKey(key)
            self._info[key1] = self.getConnectedObjs(key1) 
            return self._info[key1] #not use buffered values

    def __getattr__(self,key):
#         try:
#             return super(self.__class__,self).__getattribute__(key)
#         except:
#             log.debug("Via __getattribute__ from _info")
#             return self[key]
        
        if key in ["layout","name","_info","parsed"]:
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from _dict: %s"%key)
            return self[key]

    def __dir__(self):
        return list(dir(self.__class__)) + list(self.__dict__.keys()) + list(self.Props)

    @property
    def Info(self):
        if not self._info:
            self.parse()
            
        return self._info
    
    @property
    def Props(self):
        propKeys = list(self.Info.Keys)
        if self.maps:
            propKeys += list(self.maps.keys())
        return propKeys
    
    
    @property
    def Name(self):
        return self.name
    
    @property
    def IsPowerNet(self):
        if self.name in self.layout.nets.PowerNetNames:
            return True
        else:
            return False
    
    @property
    def IsNaming(self):
        return not re.match(r"(^N[^a-z]+)|(^UNNAMED.*)$",self.name,re.I)
    
    @property
    def Objs(self):
        return self.getConnectedObjs()
#         return self.layout.oEditor.FindObjects('Net',self.Name)
    
    def parse(self):
        if self.parsed:
            return
        self._info = ComplexDict()
        maps = self.maps
        for t in self.objTypes:
            self._info.update(t, None)
            if " " in t:
                maps[t.replace(" ","")] = t
        self._info.setMaps(maps)
        self.parsed = True
    
    def getConnectedPins(self):
        return self.getConnectedObjs('pin')

    
    def getConnectedComponnets(self):
        return self.getConnectedObjs('component')

    
    def getConnectedPorts(self):
        return self.getConnectedObjs('Port')

    
    def getConnectedObjs(self,typ = None):
        if typ:
            return self.layout.oEditor.FilterObjectList('Type', typ, self.layout.oEditor.FindObjects('Net', self.Name))
        else:
            return self.layout.oEditor.FindObjects('Net',self.Name)
    
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

        segLens = [Unit(o.TotalLength) for o in lines]
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
            
    def renameNet(self,newNet):
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

class Nets(object):

    def __init__(self,layout=None):
        '''Initialize Component object
        Args:
            compName (str): refdes of component in PCB, optional
            layout (PyLayout): PyLayout object, optional
        '''
        
#         self._netList = None
        self.netDict = None
        
        self.layout = layout
            

    def __getitem__(self, key):
        """
        key: str, regex, list, slice
        """
        
        if isinstance(key, int):
            return self.NetDict[key]
        
        if isinstance(key, slice):
            return self.NetDict[key]
        
        if isinstance(key, str):
            return self.NetDict[key]
            
#             nets = [name for name in self.NetDict.Keys if re.match(r"^%s$"%key,name,re.I)]
#             if not nets:
#                 raise Exception("not found net: %s"%key)
#             
#             #非正则表达式，返回器件自身
#             if len(nets) == 1:
#                 return self.NetDict[nets[0]]
#             else:
#                 #如果找到多个器件（正则表达式），返回列表
#                 return self[nets]
        
        if isinstance(key, (list,tuple)):
            return [self[i] for i in list(key)]
    
    def __getattr__(self,key):
        try:
            return super(self.__class__,self).__getattribute__(key)
        except:
            log.debug("Nets __getattribute__ from _info: %s"%str(key))
            return self[key]
    
    def __contains__(self,key):
        return key in self.NetDict 
            
    def __len__(self):
        return len(self.NetDict)
            
    @property
    def oProject(self):
        return self.layout.oProject
    
    @property
    def oDesign(self):
        return self.layout.oDesign
    
    @property
    def oEditor(self):
        return self.layout.oEditor 
    
    @property
    def NetDict(self):
        if self.netDict is None:
            self.netDict = ComplexDict(dict([(name,Net(name,layout=self.layout)) for name in self.oEditor.GetNetClassNets('<All>')]))
        return self.netDict
    
    @property
    def All(self):
        return self.NetDict
    
    @property
    def Names(self):
        return self.NetDict.Keys
    
    
    def getByLayer(self,layerName):
        '''
        type: [] or str
        '''
        objsLayer = self.layout.oEditor.FilterObjectList('Layer', layerName, self.layout.oEditor.FindObjects('Type',"port"))
        objsPolys = list(self.filter(lambda x: x.name in objsLayer))
        return objsPolys
    
    def refresh(self):
        self.PortDict  = None
        
    def push(self,name):
        self.NetDict.update(name,Net(name,layout=self.layout))
    
    def pop(self,name):
        del self.NetDict[name]
    
    @property
    def NetNames(self):    
        return self.NetDict.Keys
    
    @property
    def SignalNetNames(self):
        allNets = self.oEditor.GetNetClassNets('<All>')
        pwrNets = self.oEditor.GetNetClassNets('<Power/Ground>')
        sigNets = [net for net in allNets if net not in pwrNets]
        sigNets.remove("<NO-NET>")
        return sigNets
        
    @property
    def PowerNetNames(self):
        return self.oEditor.GetNetClassNets('<Power/Ground>') 
            
    #--- for Nets
    
    def getComponentsOnNets(self,nets,ignorRLC = True):
        
        if isinstance(nets, str):
            nets = [nets]
        
        temp = []
        for net in nets:
#             compNames = self.__class__(net).CompNames
            compNames = self.NetDict[net].getConnectedComponnets()
            if ignorRLC:
                compNames = [c for c in compNames if self.layout.Components[c].Type not in ["Resistor","Inductor","Capacitor"]]
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
             
        self.oEditor.CreatePortsOnComponentsByNet(
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
            nets += filter(lambda x: re.match(regNet+"$",x,re.IGNORECASE),self.NetNames)
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
                    self.layout.Nets[pnet].renameNet(nnet+tail)
                if re.match(r"^(N?\d+$)|(UNNAMED.*)|(\$.*)",nnet,re.I) and re.match(r"^N?[a-z0-9_]+[a-z]+",pnet,re.I): 
                    log.info(comp.Name+" Nets: "+ pnet + " " + nnet + ": Rename "+ nnet + " to " + pnet+tail)
                    self.layout.Nets[nnet].renameNet(pnet+tail)