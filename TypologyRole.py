from FakeRole import *

class TypologyRole:
    def __init__(self, typeId, systemId, roleId, name):
        self.typeId = typeId
        self.systemId = systemId
        self.roleId = roleId
        self.name = name
    
    def __str__(self):
        return f"<TypologyRole typeId={self.typeId} systemId={self.systemId} roleId={self.roleId} name='{self.name}'>"
    
    def toFakeRole(self):
        return FakeRole(self.roleId, self.name)