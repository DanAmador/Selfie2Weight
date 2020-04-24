import logging

logging.basicConfig(level=logging.DEBUG)
# Create handler
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.ERROR)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
dataset_logger = logging.getLogger('crawler')
# Add handlers to the logger
dataset_logger.addHandler(c_handler)
dataset_logger.addHandler(f_handler)
logging.getLogger().setLevel(logging.DEBUG)


