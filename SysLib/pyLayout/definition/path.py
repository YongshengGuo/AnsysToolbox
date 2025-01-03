#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20241219



'''Path Object

'''


import re
from ..common.common import log,regAnyMatch
from ..common.complexDict import ComplexDict


class Node(ComplexDict):
    '''
    Composed of pins objects
    node Type: VRM,Sink, Mid, Start, End
    '''
    maps = {}
    def __init__(self,node):
        
        if isinstance(node,Node):
            return node
        elif isinstance(node,(list,tuple)):
            component,net = node
        else:
            log.exception("node must be Node,list,tuple")
            
        super(self.__class__,self).__init__()
#         self.update("Pins",[])
        self.updates({
            "Component":component,
            "Net": net,
            "Type":"Mid", #Start, Mid, End
            "Previous":[],
            "Next":[]
            })
        
        self.update("self", self)
        
        maps = {"name":{
            "Key":"self",
            "Get":lambda s:"%s:%s"%(s.Component,s.Net)
            }}
        self.setMaps(maps)


class Path(object):
    '''_summary_
    '''
    
    def __init__(self,startNode = None, endNodes = None,includeComps=None,excludedNets=None,layout=None):
        self._startNode = startNode
        self._endNodes = endNodes
        if excludedNets:
            self.excludedNets = excludedNets
        else:
            self.excludedNets = [".*GND"]
        
        if includeComps:
            self.includeComps = includeComps
        else:
            self.includeComps = []

        self.PTH = ["R.*","L.*","FB.*"]
        
#         self.maxRes = 50
        self.maxPinCount = 4
        
        self.layout = layout
        self.nodes = []
        
#     def addNode(self,node):
#         self.nodes.append(node)
    
    @property
    def startNode(self):
        return self._startNode
    @startNode.setter
    def startNode(self,node):
        self._startNode = Node(node)
    
    @property
    def endNodes(self):
        return self._endNodes
    @endNodes.setter
    def endNodes(self,nodes):
        
        #remove dumplicate node
        path = Path()
        for node in nodes:
            path.insertNode(Node(node)) #will remove dumplicate node automation
        self._endNodes = path.nodes
    
    @property
    def nets(self):
        return list(set([n.net for n in self.nodes]))
    
    @property
    def comps(self):
        return list(set([n.Component for n in self.nodes]))
    
    def insertNode(self,node,loc=None,pos="Next"):
        
        if len(self.nodes)==0:
            log.info("Add node %s as start node."%node.name)
            node.Type = "Start"
            self.nodes.append(node)
            return
        
        if self.hasNode(node):
            log.info("Node already in the path: %s"%node.name)
            return
        else:
            self.nodes.append(node)
        

        
        if not loc:
            loc = self.nodes[0]

        if pos.lower() == "next":
            loc.Next.append(node)
            node.Previous.append(loc)
        elif pos.lower() == "previous":
            loc.Previous.append(node)
            node.Next.append(loc)
    
        else:
            log.info("insert node pos must be Next or Previous, input %s"%pos)
            
    
    def removeNode(self,node):
        log.info("Remove node %s"%node.name)
        self.nodes.remove(node)
        for node2 in node.Next:
            node2.Previous.remove(node)
        for node2 in node.Previous:
            node2.Next.remove(node)
    def hasNode(self,node):
        for node2 in self.nodes:
            if node.name == node2.name:
                return True
        
        return False
    
    def search(self):
        if not self.startNode:
            log.info("StartNode must set before search path.")
            return None
        if not self.endNodes:
            log.info("EndNodes must set before search path.")
            return None
        log.info("Search path from %s to %s"%(self.startNode.name,self.endNodes[0].name))
        self.nodes = []
        self.nodes.append(self.startNode) 
        self.startNode.Type = "Start"
        self._searchPath()
        self.removeInvalidNodes()

    def removeInvalidNodes(self):
        flag = True
        while(flag):
            flag = False
            for node in self.nodes:
                if node.Type.lower() in ["end","start"]:
                    continue
                
                if not node.Next or not node.Previous:
                    self.removeNode(node)
                    flag = True
    
    def _searchPath(self,startNode=None,endNodes=None):
        
        if not startNode:
            startNode = self.startNode
            
        if not endNodes:
            endNodes = self.endNodes
        
        net = startNode.Net
        startComp = startNode.Component
        endComps = [node.Component for node in endNodes]
        
        #layout.oEditor.FilterObjectList('Type','component',layout.oEditor.FindObjects('Net','BST_V1P5_S5')) 
        #return error components
    #     comps = layout.Nets[net].Objects.Components
        pins = self.layout.Nets[net].Objects.Pins
        comps = [self.layout.Pins[p].CompName for p in pins]
        comps = list(set(comps))
        
        
        newComps = []
        #comp is refdes
        for comp in comps:
            if comp == startComp:
                continue
            
            #if capacitor, ignor
            if self.layout.Components[comp].PartType in ["Capacitor"]:
                continue
            
            #include comps in includeComps for first
            if comp in self.includeComps:
                newComps.append(comp)
                continue
            
            #if is endComps, remove
            flag = False
            for node in endNodes:
                if node.Component == comp and node.Net == net:
                    # newNode = Node(comp,net)
                    node.Type = "End"
                    node.Previous = []
                    node.Next = []
                    self.insertNode(node,startNode,pos="Next")
                    flag = True
                    break
            if flag:
                endNodes = [node for node in endNodes if not (node.Component == comp and node.Net == net)]
                continue
            
            #ingor comps with more than maxPinCount
            if self.layout.Components[comp].PinCount>self.maxPinCount:
                continue            
            
            #if comp in PTH
            if regAnyMatch(self.PTH,comp):
                newComps.append(comp)
            
        if not newComps:
            return 
        
        for comp in newComps:
            for newNet in self.layout.Components[comp].NetNames:
                if newNet == net:
                    continue
                if regAnyMatch(self.excludedNets,newNet):
                    continue
                
                newNode = Node([comp,newNet])
                self.insertNode(newNode,startNode)
                self._searchPath(newNode, endNodes)

    def printTree(self,startNode=None,prefix='    '):
        if not startNode:
            startNode = self.startNode
            log.info("Power Tree:")
            log.info(startNode.name)
        # 遍历所有项
        
        if not startNode.Next:
            return

        for item in startNode.Next:
            log.info("%s|__ %s"%(prefix,item.name))
            self.printTree(item, prefix + '    ')
     

def searchPath(startNode,endNodes,layout,PTH=["R.*","L.*"],excludedNets = [".*GND"],path=None):
    if not path:
        path = Path()
        path.insertNode(startNode)
    
    net = startNode.Net
    startComp = startNode.Component
    endComps = [node.Component for node in endNodes]
    
    #layout.oEditor.FilterObjectList('Type','component',layout.oEditor.FindObjects('Net','BST_V1P5_S5')) 
    #return error components
#     comps = layout.Nets[net].Objects.Components
    pins = layout.Nets[net].Objects.Pins
    comps = [layout.Pins[p].CompName for p in pins]
    comps = list(set(comps))
    
    
    newComps = []
    
    #comp is refdes
    for comp in comps:
        if comp == startComp:
            continue
        
        #if is endComps, remove
        if comp in endComps:
            newNode = Node(comp,net)
            newNode.Type = "End"
            path.insertNode(newNode,startNode,pos="Next")
            
            if comp in endComps:
                endNodes = [node for node in endNodes if node.Component != comp]
            continue
        
        #if comp in PTH
        if regAnyMatch(PTH,comp):
            newComps.append(comp)
        
#         for each in PTH:
#             if re.match(each+"$", comp):
#                 #add new comps
#                 newComps.append(comp)
    
    if not newComps:
        return path
    
    for comp in newComps:
        for newNet in layout.Components[comp].NetNames:
            if newNet == net:
                continue
            if regAnyMatch(excludedNets,newNet):
                continue
            
            newNode = Node(comp,newNet)
            path.insertNode(newNode,startNode)
            searchPath(newNode, endNodes, layout,PTH,excludedNets,path)
    
    return path

        