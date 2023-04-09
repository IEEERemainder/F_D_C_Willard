from core.Util import Util as u

class SafeQueryConf:
    def __init__(self, badOpCodes, allowedFuncs):
        self.badOpCodes = badOpCodes
        self.allowedFuncs = allowedFuncs

    def check(self, explainData):
        OPCODE_VALUE = 1
        OPCODE_POS = 0
        FUNCTION_DATA = 5

        bad = u.scan(explainData, lambda x: r[OPCODE_VALUE] in self.badOpCodes)

        if bad:
           raise AccessError(f"SecurityError: unsafe opcode '{bad[OPCODE_VALUE]}' at pos {bad[OPCODE_POS]}") 

        badfunc = u.scan(explainData, 
            lambda r: r[OPCODE_VALUE] == "Function" 
                and not u.scan(self.allowedFuncs, lambda f: f.startswith(r[FUNCTION_DATA].lower()))
        )

        if badfunc:
            raise AccessError("SecurityError: probably unsafe function" + 
                f"{self.extractFuncName(badfunc[FUNCTION_DATA])} at pos {bad[OPCODE_POS]}"
            )
            
    def extractFuncName(self, v):
        return v[:v.index('(')]
