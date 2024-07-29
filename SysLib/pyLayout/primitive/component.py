#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410
"""
    Examples:
        >>> cmp = Component()
        >>> cmp["U1"]
        返回U1的Component对象
        
        >>> cmp[["U1","U2"]]
        返回U1,U2的Component对象List
        
        >>> cmp["U\d+"]
        返回"U\d+"匹配命名的Component对象List，匹配U1,U2,Uxxx
        
        >>> for c in layout.Components:
        >>>     log.debug(c.Name)
        打印PCB上所有的器件名字     


get component information from oEditor.GetComponentInfo API

"ComponentInfo":['ComponentName=U2', 'PartName=metal5_U2', 'ComponentType=Other', 'PlacementLayer=metal5', 
    "ComponentProp=ComponentProp(CompPropEnabled=true, Pid=-1, Pmo='0', CompPropType=2, 
    PinPairRLC(RLCModelType=0), SolderBallProp(sbsh='None', sbh='0', sbr='0', sb2='0', sbn=''), 
    PortProp(rh='0', rsa=true, rsx='0', rsy='0'))", 'LocationX=0', 'LocationY=0', 'BBoxLLx=0.002252728', 
    'BBoxLLy=0.00879525', 'BBoxURx=0.003799791', 'BBoxURy=0.0093079', 'Angle=0', 'Flip=false', 'Scale=1']
    
    BBox = (self._info["BBoxLLx"],self._info["BBoxLLy"],self._info["BBoxURx"],self._info["BBoxURy"])
"""


import re
import os
from ..common import hfss3DLParameters
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common.unit import Unit
from ..common.common import log

from collections import Counter
from .primitive import Primitive,Primitives


class Component(Primitive):
    '''

    Args:
        object (_type_): _description_
        
    Examples:
        >>> cmp = Component()
        >>> cmp["U1"]
        返回U1的Component对象
        
        >>> cmp[["U1","U2"]]
        返回U1,U2的Component对象List
        
        >>> cmp["U\d+"]
        返回"U\d+"匹配命名的Component对象List，匹配U1,U2,Uxxx
        
        >>> for c in layout.Components:
        >>>     log.debug(c.Name)
        打印PCB上所有的器件名字     
        
    '''

    def __init__(self,name = None,layout=None):
        '''Initialize Component object
        Args:
            compName (str): refdes of component in PCB, optional
            layout (PyLayout): PyLayout object, optional
        '''
        super(self.__class__,self).__init__(name,layout)




    def parse(self, force = False):
        if self.parsed and not force:
            return
        
        super(self.__class__,self).parse(force) #initial component properties
        
        comp = self.name
        componentInfo = self.layout.oEditor.GetComponentInfo(comp)
        maps = self.maps.copy()
        
        for k,v in filter(lambda x:len(x)==2,[i.split("=",1) for i in componentInfo]):
            self._info.update(k,v)
            
        self._info.update("BBox", (self._info["BBoxLLx"],self._info["BBoxLLy"],self._info["BBoxURx"],self._info["BBoxURy"]))
        
        
        #pins information will update when they used by self[]
        maps.update({"PinNames":{
            "Key":"self",
            "Get":lambda s:s.layout.oEditor.GetComponentPins(s.name)
            }})
        
        #pins objects
        maps.update({"Pins":{
            "Key":"self",
            "Get":lambda s:[s.layout.Pins[name] for name in s.layout.oEditor.GetComponentPins(s.name)]
            }})
        
        
        maps.update({"NetNames":{
            "Key":"self",
            "Get":lambda s: list(set([s.layout.Pins[p].Net for p in s.layout.oEditor.GetComponentPins(s.name)]))
            }})
        
        maps.update({"Nets":{
            "Key":"self",
            "Get":lambda s: [s.layout.Nets[name] for name in set([s.layout.Pins[p].Net for p in s.layout.oEditor.GetComponentPins(s.name)])]
            }})
        
        self._info.setMaps(maps)
        self.parsed = True


    def changePartType(self,type = "IO"):
        '''
        Args:
            typ (str, optional): Capacitor,Inductor,Resistor,IC,IO,Other . Defaults to "IO".
        '''

        self.layout.oEditor.ChangeProperty(
          [
            "NAME:AllTabs",
            [
              "NAME:BaseElementTab",
              [
                "NAME:PropServers"
              ]+[self.name],
              [
                "NAME:ChangedProps",
                [
                  "NAME:Part Type",
                  "Value:="    , type
                ]
              ]
            ]
          ])
        
        self.Info["ComponentType"] = type
        
    def createSolderBall(self,size = None ,solderMaterial = "solder", pecSize = ""):
        """
        size = Height,width,Mid
        size = ["14mil","14mil"] or [Auto,Auto]
        "SolderBallProp:=",["sbsh:=",typ,  "sbh:=",size[0],  "sbr:=",size[1],  "sb2:=",size[2],  "sbn:=",solderMaterial],
        
        """
        log.info("Create solderball on component: %s, size: %s"%(self.name,str(size)))        
            
        if size==None or str(size[0]).lower()=="auto" or str(size[1]).lower()=="auto":
            pskNames = []
            for pin in self.Pins: #[:20]
                pskNames.append(pin["Padstack Definition"])
            
            count = Counter(pskNames)
            pskName = count.most_common(1)[0][0] #find most padstack
            psk = self.layout.PadStacks[pskName]
            layerName = self["PlacementLayer"]
            pskl = psk[layerName]
            if not pskl:
                pskl = ArrayStruct(psk["psd/pds"][1])
            shp = pskl.pad.shp
            szs = pskl.pad.Szs
            
            if shp == "Rct":
                size1 = (Unit(szs[0])).V if (Unit(szs[0])).V< (Unit(szs[1])).V else (Unit(szs[1])).V
            elif  shp == "Cir":
                size1 = (Unit(szs[0])).V
            elif  shp == "Sq":
                size1 = (Unit(szs[0])).V
            else:
                log.exception("pad shape unknown: %s"%shp)
            
            
#             size2 = [(Unit(size1)*0.7)["mm"],(Unit(size1)*0.6)["mm"]] #Height 0.7x from solder, width 0.6x from aedt
            size2 = [(Unit(size1)*self.layout.options["H3DL_solderBallHeightRatio"])["mm"],(Unit(size1)*self.layout.options["H3DL_solderBallWidthRatio"])["mm"]] #Height 0.7x from solder, width 0.6x from aedt
            
            #20231106 for [Auto,Auto]
            if size[0].lower()=="auto" :
                size[0] = size2[0] 
                
            if size[1].lower()=="auto" :
                size[1] = size2[1] 
                
            if size==None:
                size = size2
                log.info("Create solderball on component: %s, size: %s"%(self.name,str(size)))

        
        
        ary = ArrayStruct(hfss3DLParameters.solderBall).copy()
        solder = ary["BaseElementTab/ChangedProps/Model Info/Model/IOProp/SolderBallProp"]
        
        if len(size) == 2:
            solder["sbsh"] = "Cyl"
            solder["sbh"] = size[0]
            solder["sbr"] = size[1]
            solder["sb2"] = size[1]
            solder["sbn"] = solderMaterial
            ary["BaseElementTab/ChangedProps/Model Info/Model/IOProp/SolderBallProp/sbn"] = solderMaterial
            
        if len(size) == 3:
            solder["sbsh"] = "Sph"
            solder["sbh"] = size[0]
            solder["sbr"] = size[1]
            solder["sb2"] = size[2]
            solder["sbn"] = solderMaterial

        PropServers = ary["BaseElementTab/PropServers"]
        PropServers.Array[1] = self.name
        #change the type to IO
        self.changePartType("IO")
        self.layout.oEditor.ChangeProperty(ary.Array)

    
    def updateRLCModel(self,**kwargs):
        '''
        {Name: R1, Part: RES_0402_100ohm, Type: Resistor, Model: filepath, RLC: [R,L,C]}
        '''
        info = ComplexDict(kwargs)       
        
        
   
    def updateModel(self,info):
        '''
        Args:
            info(list): information of component in BOM
       - {Name: R1, Part: RES_0402_100ohm, Type: Resistor, Model: filepath, RLC: [R,L,C]}

        '''
        Name = info['Name']
        RLC = info['RLC']
        Part = info['Part']
        filepath = info['Model']
        
        if filepath:
            fileType = os.path.splitext(file)[-1]
            if fileType in ['.lib','.sp','.inc']:
                #addSpiceModel
                self.addSpiceModelforCom(Name,Part,filepath)
        elif RLC:
            #changeRLCValue
            self.changeRLCValue(Name,RLC)
        else:
            pass
    
    def changeRLCValue(self,comName,rlcValue,isParallel=True):
        '''
        Args:
            rlcValue(list): RLC value [r,l,c]
            layerNum: the number of the component palcement layer (e.g. Top = 2 if slodermask exist)
        '''
        self.layout.oEditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    [
                        "NAME:PropServers", 
                        comName
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Model Info",
                            [
                                "NAME:Model",
                                "RLCProp:=", ["CompPropEnabled:=", True,                            
                                              "Pid:=", 17,                            
                                              "Pmo:=", "0",                            
                                              "CompPropType:=", 0,                            
                                              "PinPairRLC:=", ["RLCModelType:=", 0,                                
                                                               "ppr:="    , ["p1:=", "1",                                    
                                                                             "p2:=", "2",                                    
                                                                             "rlc:=", ["r:=", str(rlcValue[0]),                                        
                                                                                       "re:=", True,                                        
                                                                                       "l:=", str(rlcValue[1]),                                        
                                                                                       "le:=", True,                                        
                                                                                       "c:=", str(rlcValue[2]),                                        
                                                                                       "ce:=", True,                                        
                                                                                       "p:=", isParallel,                                        
                                                                                     #"lyr:=", layerNum
                                                                                     ]
                                                                           ]
                                                               ]
                                              ],
                                "CompType:="        , 1
                            ]
                        ]
                    ]
                ]
            ])

    def addSpiceModelforCom(self,comName,comPart,filePath):
        sktName,node1,node2 = self.readSubcktNodes(filePath)
        
        oDefinitionManager = self.oProject.GetDefinitionManager()
        oModelManager = oDefinitionManager.GetManager("Model")
        oModelManager.Add(
            [
                "NAME:"+ comPart,
                "Name:="        , comPart,
                "ModTime:="        , 1684684528,
                "Library:="        , "",
                "LibLocation:="        , "Project",
                "ModelType:="        , "dcirspice",
                "Description:="        , "",
                "ImageFile:="        , "",
                "SymbolPinConfiguration:=", 0,
                [
                    "NAME:PortInfoBlk"
                ],
                [
                    "NAME:PortOrderBlk"
                ],
                "filename:="        , filePath,
                "modelname:="        , comPart
            ])
        oDesign = self.oProject.GetActiveDesign()
        oEditor = oDesign.GetActiveEditor("Layout")
        oEditor.UpdateModels(
            [
                "NAME:ModelChanges",
                [
                    "NAME:UpdateModel0",
                    [
                        "NAME:ComponentNames", 
                        comName
                    ],
                    "Prop:="        , [    "CompPropEnabled:="    , True,
                                        "Pid:=", -1,    
                                        "Pmo:=", "0",
                                        "CompPropType:=", 0,
                                        "PinPairRLC:=", ["RLCModelType:=", 4,
                                                         "SPICE_file_path:=", filePath,                    
                                                         "SPICE_model_name:="    , comPart,                    
                                                         "SPICE_subckt:="    , sktName,                    
                                                         "terminal_pin_map:=", [node1 + ":=", "1",    node2 + ":=", "2"]]]
                ]
            ])
        

    def createPortOnNets(self,nets):
        '''
        create port on each pin of nets.
        '''
        if isinstance(nets, str):
            nets = [nets]
            
        self.layout.oEditor.CreatePortsOnComponentsByNet(
            ["NAME:Components",self.name],["NAME:Nets"]+nets, "Port", "0", "0", "0")
    
    def createPinGroup(self,groupName,pins):
        '''
        pins(list)
        '''
        self.layout.oEditor.CreatePinGroups(
            [
                "NAME:PinGroupDatas",
                [
                    "NAME:%s"%groupName, 
                ] + pins
            ])
        
    def deletePinGroup(self,groupName):
        self.layout.oEditor.Delete([groupName])
        
        
    def createPinGroupByNet(self,groupName,net):
        '''
        pins(list)
        '''
        pins = [p.Name for p in self.Pins if p.Net == net]
        
        self.layout.oEditor.CreatePinGroups(
            [
                "NAME:PinGroupDatas",
                [
                    "NAME:%s"%groupName, 
                ] + pins
            ])
        
    
    def createPinGroupPort(self,posGroup,refGroup,portZ0 = "0.1ohm"):
        '''
        posGroup is port Name
        return portName
        '''
        
        self.layout.oEditor.CreatePinGroupPort(
            [
                "NAME:elements",posGroup,
                [
                    "NAME:Boundary Types", 
                    "Port"
                ],
                [
                    "NAME:Magnitudes", 
                    str(portZ0)
                ]
            ])
        self.layout.oEditor.AddPinGroupRefPort([posGroup], [refGroup])
        return posGroup


    def createPinGroupPortOnNets(self,posNet,refNet,portZ0 = "0.1ohm"):
        '''
        Port_posNet is port Name
        '''
        posGroup = self.createPinGroupByNet("Port_%s"%posNet, posNet)
        refGroup = self.createPinGroupByNet("Port_%s"%refNet, refNet)
        return self.createPinGroupPort(posGroup, refGroup, portZ0)

    def removeAllPorts(self):
        self.layout.oEditor.RemovePortsOnComponents(
            [
                "NAME:elements", 
                self.Name
            ])
        
    def dissolve(self):
        self.layout.oEditor.DissolveComponents(["NAME:elements",self.Name])
        self.layout.Components.pop(self.Name)
        
    def delete(self):
        self.layout.oEditor.Delete([self.Name])
        self.layout.Components.pop(self.Name)
        

#not use
class Components(Primitives):
#     layout=None
    
    def __init__(self,layout=None):
        super(self.__class__,self).__init__(layout, type="component",primitiveClass=Component)
    
    def updateModels(self,modelList):
        '''
        Args:
            modelList(list): information of component in BOM
       - {Name: R1, Part: RES_0402_100ohm, Type: Resistor, Model: filepath, RLC: [R,L,C]}

        '''
        Name = modelList['Name']
        RLC = modelList['RLC']
        Part = modelList['Part']
        filepath = modelList['Model']
        
        if filepath:
            fileType = os.path.splitext(file)[-1]
            if fileType in ['.lib','.sp','.inc']:
                #addSpiceModel
                self.addSpiceModelforCom(Name,Part,filepath)
        elif RLC:
            #changeRLCValue
            self.changeRLCValue(Name,RLC)
        else:
            pass
        
    def importBOM(self,csvfile):
        pass
    
    
    def getComponentsByPart(self,part):
        '''
        Args:
            part (str): part name in PCB, ingor case, support regex
        Returns:
            (Component): Component object 
            
        Raises:
            part not found on PCB
        '''
        comps = []
        try:
            comps = [c for c in self.ComponentDict if re.match(part,c.Part,re.IGNORECASE)]
        except:
            log.debug("getComponentsByPart regex error: %s,try to get use string compare"%part)
            comps = [c for c in self.ComponentDict if c.Part.lower() == part.lower()]

        return comps
    

    def deleteInvalidRLC(self):
        '''
        if rlc have only one pin, will delete
        '''
        delComps = []
        for comp in self:
            if comp.PartType in ["Capacitor","Inductor","Resistor"] and len(comp.netnames)<2:
                log.info("Remove invalid RLC: %s, Pin Count %s"%(comp.Name,len(comp.PinNames)))
                #comp.delete()
                log.debug("delete invalid RLC: %s"%comp.Name)
                delComps.append(comp.Name)
            
        self.layout.oEditor.DissolveComponents(delComps)
        self.refresh()
        
    def getUniqueName(self,prefix="U"):
        for i in range(1,10000):
            name = "%s%s"%(prefix,i)
            names = self.NameList
            if name in names:
                i += 1
            else:
                break
        return name
    
    def createByPins(self,pinNames,layerName=None):
        if len(pinNames)<1:
            return None
        
        if not layerName:
            layerName = self.layout.Pins[pinNames[0]]["Start Layer"]
        else:
            layerName = self.layout.Layers[layerName].name
        
        compName = self.getUniqueName()
        compDefName = '%s_%s'%(layerName,compName)
        log.info("Component '%s' will created on layer '%s', with pins %s"%(compName,layerName,len(pinNames)))

        self.layout.oEditor.CreateComponent(
            [
                "NAME:Contents",
                "isRCS:="        , True,
                "definition_name:="    , compDefName,
                "type:="        , "Other",
                "ref_des:="        , compName,
                "placement_layer:="    , layerName,
                "elements:=", pinNames
            ])        
        self.push(compName)
        return compName
            