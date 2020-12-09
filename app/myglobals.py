import os

# debug
DEBUG = False

# folders path
topdir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
appfolder = os.path.abspath(os.path.join(topdir, "app"))
logfolder = os.path.abspath(os.path.join(topdir, "log"))
cachefolder = os.path.abspath(os.path.join(topdir, "cache"))
upgradefolder = os.path.abspath(os.path.join(topdir, "files/upgrade"))


# permissions & roles

class PERMISSIONS(object):
    # P1 required by:
    # 1.1 blue_rasp.vf_stat
    # 1.2 blue_rasp.vf_oplog
    # 1.3 blue_rasp.vf_data
    # 1.4 blue_rasp.vf_uploadrecord
    P1 = 0b00000001 or 1
    # P2 required by:
    # 2.1 blue_rasp.cmd_update_stat
    P2 = 0b00000010 or 2
    P3 = 0b00000100 or 4
    P4 = 0b00001000 or 8
    # P5 required by:
    # 5.1 api_rasp:ResourceReceiveData.put
    # 5.2 api_rasp:ResourceRaspUpgradeNotice.post
    P5 = 0b00010000 or 16
    # P6 required by:
    # 6.1 api_auth
    P6 = 0b00100000 or 32
    P7 = 0b01000000 or 64
    P8 = 0b10000000 or 128

class ROLES(object):
    # role: blue view observers
    # permission sum is 1
    VIEW = PERMISSIONS.P1
    # role: administrator with all permissions
    # permission sum is 1+2+4+8+16+32+64+128=255
    ADMIN = PERMISSIONS.P1 + PERMISSIONS.P2 + PERMISSIONS.P3 + PERMISSIONS.P4 + PERMISSIONS.P5 + PERMISSIONS.P6 + PERMISSIONS.P7 + PERMISSIONS.P8
    # role: for api_rasp, especially upload data
    API_RASP = PERMISSIONS.P5
    # role: for api_auth
    API_AUTH = PERMISSIONS.P6

# massive query per count
PER_QUERY_COUNT = 10000

# fcode table
# todo
tab_fcode = {
    # -1: 'Unknown',
    # 0: 'All',
    1: 'Leedarson',
    2: 'Innotech',
    3: 'Tonly',
    4: 'Changhong',
    5: 'TestFactory',
    6: 'Topstar',
}


# opcode table
tab_opcode = {
    1: 'upload',
    2: 'upgrade',
    3: 'download',
    4: 'update',
}

