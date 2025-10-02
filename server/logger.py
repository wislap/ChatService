import logging
from loguru import logger
import sys


class InterceptHandler(logging.Handler):
    """
    把标准 logging 的日志转发给 loguru
    """
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 找到调用日志的文件和行号
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger():
    """
    初始化日志配置，接管 FastAPI/Uvicorn 的日志
    """
    # 清理默认 handler
    logging.root.handlers = []
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # 让所有已有 logger（如 uvicorn）走 root
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # 控制台日志
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
            "| <level>{level: <8}</level> "
            "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>",
        level="TRACE",
    )

    # 文件日志（自动切割，每个 10MB，保留 7 天）
    logger.add(
        "server/logs/app.log",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        level="TRACE",
    )


# 在 import 时就初始化
setup_logger()
