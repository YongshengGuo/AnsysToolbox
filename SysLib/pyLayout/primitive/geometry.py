#coding:utf-8
#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20230410


import math
from ..common.unit import Unit
from ..common.common import log

class Point(object):
    layout = None
    def __init__(self,pt = None,layout = None, arc = False):
        '''
        pt: list,tuple,"x,y",Point, 3DL Point
        '''
        
        
        self.x = 0
        self.y = 0
        self.arc = arc
        
        if isinstance(pt, (list,tuple)):
            self.x = pt[0]
            self.y = pt[1]
        elif "ADispatchWrapper" in str(type(pt)):
            self.x = pt.GetX()
            self.y = pt.GetY()
        elif isinstance(pt, self.__class__):
            self.x = pt.x
            self.y = pt.y
        elif isinstance(pt,str):
            xy = pt.split(',')
            if len(xy)!=2:
                log.exception("Point input error %s"%pt)
            self.x = xy[0]
            self.y = xy[1]
        else:
            log.debug("Point init error")
            
        if layout:
            self.__class__.layout = layout
            
    def __getitem__(self, key):
        """
        key: int 0,1
        key: str X,Y
        """
        if isinstance(key, int):
            return [self.x,self.y][key]
        
        if isinstance(key, str):
            if key.lower() == 'x':
                return self.x
            elif key.lower() == 'y':
                return self.y
            elif key.lower() == 'xy':
                return [self.x,self.y]
            if key.lower() == 'xvalue':
                return Unit(self.x).V
            elif key.lower() == 'yvalue':
                return Unit(self.y).V
            elif key.lower() == 'xyvalue':
                return [Unit(self.x).V,Unit(self.y).V]
            
            else:
                log.exception("Point key error: %s"%key)
        
        log.exception("Point key error: %s"%str(key))
        
    def __getattr__(self,key):
        if key in ["x","y","arc"]: #not key.lower()
            return object.__getattr__(self,key)
        else:
            log.debug("__getattr__ from __getitem__: %s"%key)
            return self[key]
        
        
    def __repr__(self):
        return "Point Object: [%s,%s]"%(self.x,self.y)
        
    def __len__(self):
        return 2
        
    @property
    def H3DLPoint(self):
        pt3DL = self.layout.oEditor.Point().Set(self.x,self.y)
        if self.arc:
            pt3DL.SetArc(True)
        return pt3DL
    
    @property
    def XY(self):
        return self.x,self.y
        
    def __add__(self,u):
        if isinstance(u, self.__class__):
            x1 = Unit(self.x)
            x2 = Unit(u.x)
            y1 = Unit(self.y)
            y2 = Unit(u.y)
            
            return self.__class__([(x1+x2)[x1.unit],(y1+y2)[x1.unit]])
        else:
            return self + self.__class__(u)

    def __sub__(self,u):
        if isinstance(u, self.__class__):
            x1 = Unit(self.x)
            x2 = Unit(u.x)
            y1 = Unit(self.y)
            y2 = Unit(u.y)
            return self.__class__([(x1-x2)[x1.unit],(y1-y2)[x1.unit]])
        else:
            return self - self.__class__(u)
        
    def distanceFromPoint(self,pt):
        pt2 = self.__class__(pt)
        return ((self.x-pt2.x)**2 + (self.y-pt2.y)**2)**0.5
    
    
class Polygen(object):
    
    layout = None
    def __init__(self,pts = None,layout = None,closed = True):
        '''
        pts: [[x1,y1],[x2,y2]]
        '''
        
        self.points = []
        self.closed = closed
        if pts:
            for pt in pts:
                if isinstance(pt, Point):
                    self.points.append(pt)
                else:
                    #pt is list or tuple
                    self.points.append(Point(pt))
                    
        if layout:
            self.__class__.layout = layout
    
    @property
    def H3DLPolygen(self):
        ply = self.layout.oEditor.Polygon()
        for pt in self.points:
            ply.AddPoint(pt.H3DLPoint)
            
        if self.closed:
            ply.SetClosed(True)
        return ply
    
    def getPerimeter(self):
        n = len(self.points)
        perimeter = 0
        for i in range(n):
            x1, y1 = self.points[i].XY
            x2, y2 = self.points[(i+1) % n].XY
            side_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            perimeter += side_length
            
        return perimeter

    def getArea(self):
        n = len(self.points)
        area = 0
        for i in range(n):
            x1, y1 = self.points[i].XY
            x2, y2 = self.points[(i+1) % n].XY
            area += (x1 * y2 - x2 * y1) / 2
        return area
    
    def getCenter(self):
        x = sum([pt.x for pt in self.points])/len(self.points)
        y = sum([pt.y for pt in self.points])/len(self.points)
        return x,y

    @classmethod
    def circle(cls,center,r):
        ptCenter = Point(center)
        pts = [ptCenter-(r,0),Point([r,0],arc=True),ptCenter+(r,0),Point([r,0],arc=True)]
        return cls(pts)
        
    