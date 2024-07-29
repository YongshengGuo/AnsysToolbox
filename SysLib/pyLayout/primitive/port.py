#--- coding:utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 2023-04-24

'''
Ports manager module
'''

import re
from ..common import hfss3DLParameters
from ..common.arrayStruct import ArrayStruct
from ..common.complexDict import ComplexDict
from ..common.unit import Unit
from ..common.common import log

from .primitive import Primitive,Primitives
from .geometry import Point



def sortBus(net):
    nums = re.findall(r"\d+",net,re.I) #number
    residual = re.sub(r"[\dPNTR+-]+", "", net)
    sums = sum([float(i) for i in nums]) if nums else 1e9
    return residual,net.upper().count("R"),sums,net.upper().count("N")+net.count("-")+net.count("#")
    #R: Tx, Rx, N: P/N +/- #


class Port(Primitive):

        
    def parse(self, force = False):
        if self.parsed and not force:
            return
        
        super(self.__class__,self).parse(force) #initial component properties
        
        maps = self.maps.copy()
        EMProperties = self.layout.oEditor.GetProperties("EM Design","Excitations:%s"%self.Name)
        self._info.update("EMProperties",EMProperties)
        for prop in EMProperties:
            self._info.update(prop,None) #here give None value. get property value when used to improve running speed
            maps.update({prop.replace(" ",""):prop}) #map property with space characters

        #---prot infomation
        for item in self.layout.oEditor.GetPortInfo(self.name):
            splits = item.split("=",1)
            if len(splits) == 2:
                self._info.update(splits[0].strip(),splits[1].strip())
            else:
                log.debug("ignor port information: %s"%item)
        
        self._info.setMaps(maps)
        
    def get(self, key):
        
        if not self.parsed:
            self.parse()
        
        realKey = key
        
        if realKey in self._info.EMProperties:  #value is None
            self._info.update(realKey, self.layout.oEditor.GetPropertyValue("EM Design","Excitations:%s"%self.Name,realKey))
            return self._info[realKey]
        
        return super(self.__class__,self).get(realKey)
    
    
    
    def set(self,key,value):
        '''
        mapping key must not have same value with maped key.
        '''
        
        
        if not self.parsed:
            self.parse()
        
        realKey = self._info.getReallyKey(key)
            
        if key in self._info.EMProperties: 
            self.layout.oEditor.SetPropertyValue("EM Design", "Excitations:" + self.Name, realKey, value)
            self._info[realKey] = value
            if realKey == "Port": #Remane port name
                self.layout.Ports.refresh()
            return
#             self.parsed = False #refresh

        return super(self.__class__,self).set(key,value)
     
    def setPortImpedance(self,value):
        self.setProp("Impedance", str(value))
        self.setProp("Renormalize Impedence", str(value))
        
    def setSIwavePortRefNet(self,value):
        self.setProp("Reference Net", str(value))
        
        
    def autoRename(self):
        if "." in self.Name:
            log.info("skip port: %s"%self.Name)
            return
            
        ConnectionPoints = self.ConnectionPoints #0.000400 0.073049 Dir:270.000000 Layer: BOTTOM    
        splits = ConnectionPoints.split() #['0.000400', '0.073049', 'Dir:270.000000', 'Layer:', 'BOTTOM']
        X = float(splits[0])
        Y = float(splits[1])
        layer = splits[-1]
        posObjs = list(self.layout.getObjectByPoint([X,Y],layer = layer,radius="2mil"))
#         print(self.Name,posObjs,layer)
        
        if not posObjs:
            log.info("Not found objects on port '%s' position, skip."%self.Name)
            return

        if self.Name in posObjs:
            posObjs.remove(self.Name)
            
        if not posObjs:
            log.info("Not found objects on port '%s' position, skip."%self.Name)
            return
#             
#         posObj = posObjs[0]
        posObj = None
        for obj in posObjs:
            if obj in self.layout.Pins:
                posObj = obj
                break
            
        if not posObj:
            posObj = posObjs[0]
            
        if posObj in self.layout.Pins:   
            tempList = list(posObj.split("-"))+[self.layout.Pins[posObj].Net]
            newName = ".".join(tempList)
    #         print(newName,port)
            log.info("Rename %s to %s"%(self.Name,newName))
            self.Port = newName
        else:
            newName = self.layout[posObj].Net
            log.info("Rename %s to %s"%(self.Name,newName))
            self.Port = newName
        
        
    
class Ports(Primitives):
    
    def __init__(self,layout=None):
        super(self.__class__,self).__init__(layout, type="port",primitiveClass=Port) #port not get by FindObjects

    @property
    def ObjectDict(self):
        '''
        get all port by oDesign.GetModule("Excitations").GetAllPortsList()
        '''

        if self._objectDict is None:
            self._objectDict = ComplexDict(dict([(port,Port(port,layout=self.layout)) for port in self.layout.oDesign.GetModule("Excitations").GetAllPortsList()]))
        return self._objectDict 

    def _portOrderRule(self,port,compOrder=[],netOrder=[]):
        
        if not compOrder:
            compOrder = []
            
        if not netOrder:
            netOrder = []
        
        # X: comp.pin.net
        rules = []
        comp,pin,net = port.split('.')
        #if compOrder:
        rules.append(compOrder.index(comp) if comp in compOrder else comp)
        
        if net in netOrder:
            rules.append(netOrder.index(net))
        else:
            rules += sortBus(net)
        
        return rules

    def _getMatchPortNames(self,name):
        '''
        name: support regex
        '''
        name ="^" + name.replace("*",".*?") + "$" #.replace(".","\.") 
        return list(filter(lambda x:re.match(name, x,re.I), self.NameList))

    def reorder(self,compOrder=[],netOrder=[],portOrder = []):
        '''
        assume port is generated by 3dlayout in rules: comp.pin.net
        compOrder is None will order by alphabet
        netOrder is none will order by bus 
        portOrder: comp.pin.net, comp.*.net, *.*.net, comp.pin.*  "*" is regex
        
        if portOrder have valid value, compOrder and netOrder will be ignored.
        '''
        log.info("order ports:")
        names = self.NameList
        
        #---portOrder first
        if portOrder:
            origNames = names[:]
            orderNames = []
            for p in portOrder:
                mports = self._getMatchPortNames(p)
                for p in mports:
                    orderNames.append(p)
                    origNames.remove(p)
            
            log.info("reorder port by portOrder: %s"%(".".join(orderNames+origNames)))
            oModule = self.layout.oDesign.GetModule("Excitations")         
            oModule.ReorderMatrix(orderNames+origNames) #add residual ports     
            return orderNames+origNames
        
        
        #---compOrder and netOrder
        rulePorts = []
        unRulePorts = []
        for name in names:
            splits = name.split(".")
            if len(splits) ==3:
                rulePorts.append(name)
            else:
                log.info("unrule ports found:%s"%name)
                unRulePorts.append(name)
        
        rulePorts.sort(key= lambda p:self._portOrderRule(p, compOrder, netOrder))
        log.info("re order port %s"%(".".join(rulePorts+unRulePorts)))
        oModule = self.layout.oDesign.GetModule("Excitations")
        oModule.ReorderMatrix(rulePorts+unRulePorts)
        return rulePorts+unRulePorts
        
