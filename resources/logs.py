# logs.py
"""Contains the logger"""

import logging
import logging.handlers
import os

from resources import settings


log_file = settings.logfile
if not os.path.isfile(log_file):
    open(log_file, 'a').close()


logger = logging.getLogger('discord')
if settings.DEBUG_MODE == 'ON':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(filename=log_file,when='D',interval=1, encoding='utf-8', utc=True)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)