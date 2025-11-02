import logging
from src.now_time import today, now_time
from src.read_conf import read_conf
import sys
import os


class Log:
    def __init__(self):
        self.day = today()
        self.logger = self.setup_logger()
        self.confing = read_conf()
        self.log_level = self.confing.log_level()

    def _get_log_dir(self):
        """获取日志目录路径（兼容 exe 打包）"""
        if getattr(sys, 'frozen', False):
            # 打包后的 exe，使用 exe 所在目录
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境，使用 blankEndApi 目录
            base_path = os.path.dirname(os.path.dirname(__file__))
        
        log_dir = os.path.join(base_path, 'log')
        
        # 自动创建 log 目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"📁 已创建日志目录: {log_dir}")
        
        return log_dir

    def setup_logger(self):
        log_dir = self._get_log_dir()
        log_file = os.path.join(log_dir, f"{self.day}_blankEndApi.log")
        # 创建一个logger对象
        logger = logging.getLogger("my_logger")
        logger.setLevel(logging.DEBUG)
        # 清除现有的处理器，以防止累积
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        # 创建一个文件处理器，将日志写入文件
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        # 创建一个控制台处理器，将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        # 定义日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        # 将处理器添加到logger对象
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def write_log(self, text, log_type):
        # 输出不同级别的日志
        if self.log_level == "error":
            if log_type == 'info':
                print(f"{now_time()} - INFO - {text}")
            elif log_type == 'error':
                self.logger.error(text)
            elif log_type == 'warning':
                self.logger.warning(text)
            elif log_type == 'I':
                self.logger.info(text)
        elif self.log_level == "info":
            if log_type == 'info':
                self.logger.info(text)
            elif log_type == 'error':
                print(f"{now_time()} - ERROR - {text}")
            elif log_type == 'warning':
                self.logger.warning(text)
        elif self.log_level == "debug":
            if log_type == 'info':
                self.logger.info(text)
            elif log_type == 'error':
                self.logger.error(text)
            elif log_type == 'warning':
                self.logger.warning(text)

        elif self.log_level == "critical" and log_type == 'critical':
            self.logger.critical(text)
        # 检查是否开始了新的一天，如果是，则更新日志文件名
        new_day = today()
        if new_day != self.day:
            self.day = new_day
            # 在创建新处理器之前关闭旧的文件处理器
            self.logger.handlers[0].close()
            self.logger = self.setup_logger()


logger = Log()


def err1(e):
    logger.write_log(f"Err Message:,{str(e)}", "error")
    logger.write_log(f"Err Type:, {type(e).__name__}", "error")
    _, _, tb = sys.exc_info()
    logger.write_log(f"Err Local:, {tb.tb_frame.f_code.co_filename}, {tb.tb_lineno}", "error")
    logger.write_log(e, "error")


def err2(e):
    logger.write_log(f"Err Message:,{str(e)}", "error")
    logger.write_log(f"Err Type:, {type(e).__name__}", "error")
    _, _, tb = sys.exc_info()
    logger.write_log(f"Err Local:, {tb.tb_frame.f_code.co_filename}, {tb.tb_lineno}", "error")


def err3(e):
    pass
