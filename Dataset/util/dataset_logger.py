import logging
import sys

from loguru import logger as dataset_logger

dataset_logger.add("file.log", enqueue=True, rotation="1 week")

dataset_logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>", filter="scrapper", level="DEBUG")

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("psaw").setLevel(logging.WARNING)
#
# # Create handler
# dataset_logger = logging.getLogger('crawler')
# logging.getLogger("crawler").setLevel(logging.DEBUG)
# c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler('file.log')
# c_handler.setLevel(logging.WARNING)
# f_handler.setLevel(logging.ERROR)
#
# # Create formatters and add it to handlers
# c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)
# # Add handlers to the logger
# dataset_logger.addHandler(c_handler)
# dataset_logger.addHandler(f_handler)
# dataset_logger.setLevel(logging.DEBUG)


