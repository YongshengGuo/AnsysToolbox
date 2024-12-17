#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410



'''Net Object quick access

'''


import re
from ..common.common import log
from ..common.unit import Unit
from ..common.complexDict import ComplexDict
from ..common.arrayStruct import ArrayStruct
from .definition import Definitions,Definition

# class Terminal(ComplexDict):
#     def __init__(self):
#         super(self.__class__,self).__init__()
#         self.update("Component",None)
#         self.update("Pin",[])


class Node(ComplexDict):
    '''
    Composed of pins objects
    node Type: VRM,Sink, Mid, Start, End
    '''
    maps = {}
    def __init__(self,component=None,net=None):
#         self.update("Pins",[])
        self.updates({
            "Component":component,
            "Net": net,
            "Type":"Mid",
            "Previous":None,
            "Next":None
            })
        
        self.update("self", self)
        
        self.maps.update({"name":{
            "Key":"self",
            "Get":lambda s:"%s_%s"%(s.Component,s.Net)
            }})


class Path(object):
    '''_summary_
    '''
    
    def __init__(self,nodes = [],PTH=["R.*,L.*"],layout=None):
        self.nodes = nodes
        self.PTH = PTH
        self.layout = layout
        
#     def addNode(self,node):
#         self.nodes.append(node)
    
    def insertNode(self,loc,node,pos="Next"):
        self.nodes.append(node)
        if pos.lower() == "next":
            if isinstance(loc.Next, list):
                loc.Next.append(node)
            elif loc.Next == None:
                loc.Next = node
            else:
                loc.Next = [loc.Next,node] 
                
        elif pos.lower() == "Previous":
            loc.Previous = node
        else:
            log.info("insert node pos must be Next or Previous, input %s"%pos)

        node.Previous = loc
    
    def hasNode(self,node):
        for node2 in self.nodes:
            if node.name == node2.name:
                return True
        
        return False
    
    def getFirstNode(self):
        for node in self.nodes:
            if node.Type.lower() in ["vrm","start"]:
                return node
        return None




def getPath(startNode,endNodes,layout,PTH=["R.*,L.*"],path=None):
    if not path:
        path = []
        path.append(startNode)
    
    net = startNode.Net
    startComp = startNode.Component
    endComps = [node.Component for node in endNodes]
    
    comps = layout.Nets[startNode.Net].Objects.Components
    newComps = []
    for comp in comps:
        if comp == startComp:
            continue
        
        if comp in endComps:
            newNode = Node(comp,net)
            path.insertNode(startComp,newNode)
            endNodes = [node for node in endNodes if node.Component != comp]
            continue
        
        newComps.append(comp)
    
    if not newComps:
        return
    
    for comp in newComps:
        newNode = Node(comp,net)
        path.insertNode(startComp, newNode)
        getPath(newNode, endNodes, layout, PTH,path)

        
        
      
#for test
if __name__ == '__main__':
    startNode = Node()