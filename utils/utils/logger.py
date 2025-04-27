import logging
import logging.handlers
import os

class Logger:
    def __init__(self, name="app_logger", log_file="app.log", level=logging.DEBUG):
        """
        初始化 Logger 类
        :param name: 日志记录器的名称
        :param log_file: 日志文件路径
        :param level: 日志记录的最低级别
        """
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level)

        log_file_fullpath = os.path.abspath(log_file)
        if not os.path.exists(os.path.dirname(log_file_fullpath)):
            os.makedirs(os.path.dirname(log_file_fullpath))  # 创建目录，如果不存在

        # 创建一个按天分割的日志处理器
        timer_handler = logging.handlers.TimedRotatingFileHandler(
            log_file_fullpath,             # 日志文件路径
            when='midnight',          # 设置按午夜（00:00）分割
            interval=1,               # 每隔1天分割一次
            backupCount=7,            # 保留最近7天的日志文件
            encoding='utf-8'          # 设置日志文件编码
        )
        # 设置日志文件名后缀
        timer_handler.suffix = "%Y-%m-%d.log"  # 每天的日志文件名格式：my_log-YYYY-MM-DD.log

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建日志格式器
        formatter = logging.Formatter('[%(name)s] [%(asctime)s - %(levelname)s] %(message)s')
        timer_handler.setFormatter(formatter)  # 按天分割的日志格式
        console_handler.setFormatter(formatter)


        # 将处理器添加到日志记录器
        self.__logger.addHandler(timer_handler)
        self.__logger.addHandler(console_handler)

    @property
    def logger(self):
        """返回 Logger 实例"""
        return self.__logger

    def debug(self, msg):
        """记录调试信息"""
        self.__logger.debug(msg)

    def info(self, msg):
        """记录一般信息"""
        self.__logger.info(msg)

    def warning(self, msg):
        """记录警告信息"""
        self.__logger.warning(msg)

    def error(self, msg):
        """记录错误信息"""
        self.__logger.error(msg)

    def critical(self, msg):
        """记录严重错误信息"""
        self.__logger.critical(msg)
