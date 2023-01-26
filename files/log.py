import os.path
import logging

# Get the directory of the current python file
main_dir = os.path.realpath(os.path.dirname(__file__))

#### Set logging configurations
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
## Console logger
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)
## Simple logger
f1_handler = logging.FileHandler(os.path.join(main_dir, 'info.log'), mode='w')
f1_handler.setLevel(logging.INFO)
f1_format = logging.Formatter('%(message)s')
f1_handler.setFormatter(f1_format)
logger.addHandler(f1_handler)
## Detail logger
f2_handler = logging.FileHandler(os.path.join(main_dir, 'debug.log'), mode='w')
f2_handler.setLevel(logging.DEBUG)
f2_handler.setFormatter(c_format)
logger.addHandler(f2_handler)