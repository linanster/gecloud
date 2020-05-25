from uuid import uuid4
from datetime import datetime
import sys

version = sys.argv[1]

timestr = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

pin = uuid4().hex[0:4]






print('{}-{}-{}'.format(version, timestr, pin))
