

class FcodeNotSupportError(Exception):
    def __init__(self,fcode):
        self.fcode = fcode
        self.err_msg = "fcode ( " + str(fcode) + " ) " + " not supported"
