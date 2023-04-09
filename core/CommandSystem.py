from core.Util import Util as u

class CommandSystem:
    def __init__(self, *cmds):
        self.d = {}
        for cmd in cmds:
            self.registerCmd(cmd)

    def registerCmd(self, cmd):
        for name in cmd.names:
            self.d[name] = cmd

    def __contains__(self, item):
        return item in self.d

    def __getitem__(self, key):
        return self.d[key]
        
    def __setitem__(self, key, value):
        print("not recommended to use __setitem__ on CommandSystem")
        self.d[key] = value
