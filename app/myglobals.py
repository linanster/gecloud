import os

topdir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
appdir = os.path.abspath(os.path.join(topdir, "app"))
logdir = os.path.abspath(os.path.join(topdir, "log"))
cachefolder = os.path.abspath(os.path.join(topdir, "cache"))
upgradefolder = os.path.abspath(os.path.join(topdir, "files/upgrade"))
