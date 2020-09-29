import logging
from logging.handlers import RotatingFileHandler
import os

from  app.myglobals import logfolder


logfile = os.path.abspath(os.path.join(logfolder, "log.txt"))

# logger init
logger = logging.getLogger(__name__)


# logger config
logger.setLevel(level = logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# handler = logging.FileHandler(logfile)
handler = RotatingFileHandler(logfile, maxBytes = 1*1024*1024, backupCount=3)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)

