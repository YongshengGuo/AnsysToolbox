#coding:utf-8
'''
    ##模块功能：
    初始化日志属性、生成日志文件、返回日志文件的日志器, 可以被调用打印日志文件

    Examples:
        1.从log文件导入Log类
        >>> from log import Log
        
        2.实例化类Log()后使用其方法setPath()设置log文件完整路径
        >>> log = Log() #默认log Level是DEBUG(即全部都打印)
        >>> log = Log('Error') #指定log Level是Error, (Optional)
        
        >>> log.setPath(r'C:\Temp\logfile.log') #必须设置log文件全名称
        
        3.设置log Level (Optional)
        >>> logger.setLogLevel('Error')
                总共5个log级别,目前默认是DEBUG(即全部都打印)
        
        4.打印日志        
        >>> log.debug('debug,用来打印一些调试信息，级别最低')
        >>> log.info('info,用来打印一些正常的操作信息')
        >>> log.warning('waring,用来用来打印警告信息')
        >>> log.error('error,一般用来打印一些错误信息')
        >>> log.critical('critical,用来打印一些致命的错误信息，等级最高')

'''
import sys
import logging

class Log(object):
    # 初始化日志
    def __init__(self, logLevel='DEBUG', logPath = None):
        '''
        Args:
            >>> logLevel(str): 打印log日志的级别, 默认是DEBUG以上级别(即全部打印),optional
        '''
        self._logPath = logPath
        self._logLevel = logLevel
#         self._logFormat = '%(filename)s-%(lineno)s: - %(asctime)s - %(levelname)s: %(message)s'
        self._logFormat = '%(asctime)s - %(levelname)s: %(message)s'
        self._datefmt = "%Y/%m/%d %X"
        
        self.logger = logging.getLogger()
        self.file_handler = None
        self.console_handler = logging.StreamHandler()
        self.logger.addHandler(self.console_handler)
        self.setLogLevel(self._logLevel)
        self.setLogFormat()
        
    
    def __del__(self):
        if self.file_handler:
            self.file_handler.close()
        if self.console_handler:
            self.console_handler.close()
        logging.shutdown()
    
    
    def setLogLevel(self,logLevel=None):
        '''
        #用来设置LogLevel
        Args:
            logLevel(str): 打印log日志的级别, 默认是DEBUG以上级别(即全部打印), 字段包含CRITICAL > ERROR > WARNING > INFO > DEBUG, 不区分大小写, optional
        '''
        if logLevel:
            self._logLevel = logLevel.upper()
        
        level = eval('logging.' + self._logLevel.upper())
        self.logger.setLevel(level)
        for handle in self.logger.handlers:
            handle.setLevel(level)

        
    def setPath(self,logPath=None):
        '''
        Args:
            logPath(str): log文件完整路径
        '''
        if not logPath:
            return
        
        self.logPath = logPath
        
        if self.file_handler:
            self.file_handler.close()
            self.logger.removeHandler(self.file_handler)
            
        self.file_handler = logging.FileHandler(logPath,mode='a')
        self.logger.addHandler(self.file_handler)
        self.setLogFormat()
        self.setLogLevel()
  
            
    def setLogFormat(self,logFormat = None,datefmt = None):
        # 1、设置formatter，日志的输出格式
        if logFormat:
            self._logFormat = logFormat
        if datefmt:
            self._datefmt = datefmt
            
        fmt = logging.Formatter(self._logFormat,self._datefmt)
        for hdlr in self.logger.handlers:
            hdlr.setFormatter(fmt)
        
    def aedtMessage(self,content):
        Module = sys.modules['__main__']
        oDesktop = None
        if hasattr(Module, "oDesktop"):
            oDesktop = getattr(Module, "oDesktop")
            
        if oDesktop:
            oDesktop.AddMessage("","",0,content)
        else:
            return
        
    def debug(self,content,*args):
        self.logger.debug(content+",".join(args))
#         self.aedtMessage(content)

    def info(self,content,*args):
        self.logger.info(content+",".join(list(args)))
#         self.aedtMessage(content+",".join(args))
           
    def warning(self,content,*args):
        self.logger.warning(content+",".join(args))
        self.aedtMessage(content+",".join(args))
            
    def error(self,content,*args):
        self.logger.error(content+",".join(args))
        self.aedtMessage(content+",".join(args))
           
    def critical(self,content,*args):
        self.logger.critical(content+",".join(args))
        self.aedtMessage(content+",".join(args))
        
    def exception(self,content,*args):
        if isinstance(content, str):
            content = Exception(content+",".join(args))
            self.logger.error(content)
            raise content

    #for debug
    def messageBox(self,content):
        from System.Windows.Forms import MessageBox
        MessageBox.Show(str(content))
        