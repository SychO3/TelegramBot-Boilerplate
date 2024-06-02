import os
from loguru import logger

# 删除已存在的日志文件
try:
    os.remove("logs.txt")
except BaseException:
    pass

# 配置 loguru 日志记录器
logger.add(
    "logs.txt",
    rotation="5 MB",  # 当日志文件达到5 MB时自动创建新文件
    retention="10 days",  # 保留日志文件10天
    compression="zip",  # 将旧的日志文件压缩成zip格式
    level="INFO",
)


def log(name: str = None):
    # 这个函数通过loguru来绑定一个额外的上下文，以模仿传统的命名日志记录器
    return logger.bind(name=name)
