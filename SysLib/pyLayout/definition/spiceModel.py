#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com
#--- @Time: 20230410

from ..common.common import log,readData

class Subckt(object):
    def __init__(self,path):
        self.path = path
        self.name = ""
        self.nodes = []
        
        if path:
            self.parse()
        
    def parse(self, path=None):
        """
        解析给定路径下的电路描述文件，并提取.subckt行以及其节点信息。
        
        参数:
        - path: str, 文件路径。如果未提供，则使用self.path。
        
        没有返回值，但更新self.name和self.nodes属性。
        """
        # 确定要读取的文件路径
        path = path or self.path
        # 读取文件内容
        datas = readData(path)
        
        # 初始化存储每行数据的列表
        lines = []
        # 分行处理数据
        for l in datas.splitlines():
            # 去除行首尾的空白字符
            line = l.strip()
            # 跳过空行
            if not line:
                continue
            
            # 跳过以"*"开头的行
            if line.startswith("*"):
                continue
            
            # 处理以"+"开头的行，将其余下部分与上一行合并
            if line.startswith("+"):
                if not lines:
                    continue
                lines[-1] += " " + line[1:]
                continue
            
            # 将处理后的行添加到lines列表中
            lines.append(line)
        
        # 查找.subckt行
        header = ""
        for line in lines:
            if line.lower().startswith(".subckt"):
                header = line
                break
        
        # 分割header行，提取子电路的名称和节点
        splits = header.split()
        self.name = splits[1]
        self.nodes = splits[2:]
        

    