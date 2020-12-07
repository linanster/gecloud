

class FcodeNotSupportError(Exception):
    def __init__(self,fcode):
        self.fcode = fcode
        self.err_msg = "fcode ( " + str(fcode) + " ) " + " not supported"

class OpcodeNotSupportError(Exception):
    def __init__(self,opcode):
        self.opcode = opcode
        self.err_msg = "opcode ( " + str(fcode) + " ) " + " not supported"
