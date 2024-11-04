#--- coding=utf-8
#--- @Author: Yongsheng.Guo@ansys.com, Henry.he@ansys.com,Yang.zhao@ansys.com
#--- @Time: 20240830


'''
read and get config in excel
'''
import sys
isIronpython = "IronPython" in sys.version

class XlsReader(object):
    
    def __init__(self,path):
        self.path = path
        self.sheetDict = None
        
        
    def getSheetData(self, path=None, sheetName=0):
        '''
        根据指定的路径和工作表名称获取数据。
        
        参数:
        - path: str, Excel文件的路径，默认为None，表示使用类的默认路径。
        - sheetName: int, str, list, or None, 默认为0。
        工作方式:
        - 默认值为0: 返回第一个工作表作为DataFrame。
        - 1: 返回第二个工作表作为DataFrame。
        - "Sheet1": 加载名称为“Sheet1”的工作表。
        - [0, 1, "Sheet5"]: 加载第一个、第二个以及名称为“Sheet5”的工作表，作为DataFrame字典。
        - None: 加载所有工作表。
        - return list 
        '''
        # 如果路径未提供，则使用类的默认路径
        path = path or self.path
        
        # 导入pandas库，用于数据处理
        import pandas as pd
        # 读取Excel文件，这里假设文件名为'example.xlsx'
        # 可以指定要读取的工作表名称
        df = pd.read_excel(path, sheet_name = sheetName)
        df = df.applymap(lambda x: str(x).strip() if str(x).strip() != "nan" else "") #转化为字符串
        # 将DataFrame转换为列表
        datas = list(df.to_dict(orient='index').values())
        return datas
    
    def getAllSheetData(self, path=None):
        '''
        获取Excel文件中的所有工作表数据。
        
        参数:
        - path: str, Excel文件的路径，默认为None，表示使用类的默认路径。
        
        返回:
        - dict: 包含所有工作表数据的字典。键为工作表名称，值为对应的DataFrame。
        '''
        # 如果路径未提供，则使用类的默认路径
        path = path or self.path
        # 导入pandas库，用于数据处理
        import pandas as pd
        # 读取Excel文件，这里假设文件名为'example.xlsx'
        # 可以指定要读取的工作表名称
        df_all = pd.read_excel(path, sheet_name = None)
        # 将DataFrame转换为列表
        for key in df_all:
            df = df_all[key]
            df = df.map(lambda x: str(x).strip() if str(x).strip() != "nan" else "") #转化为字符串
            df_all[key] = list(df.to_dict(orient='index').values())
        return df_all

    def readAll(self):
        return self.getAllSheetData()
    
    
if __name__ == '__main__':
    path = r"C:\work\Project\Pre_support\Honor\PSI_script_0719\SIWAVE_TEST_CASE\SIWAVE_PDN_20240716.xlsx"
    xls = XlsReader(path)
    datas = xls.getAllSheetData()
    print(datas)
