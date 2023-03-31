from TypologyRole import *
from SQLiteWrapper import *
from Util import Util as u

class TypologiesRoleSystem:
    def __init__(self):
        self.db = SQLiteWrapper(r"C:\Users\Paul\root\db\typologiesTypes.db")
        self.allRoles = self.getAllRoles()
        self.availableRoles = self.getAvailableRoles()

    def getAllRoles(self):
        return self.db.exep("SELECT id, systemId, type FROM types", [], lambda x: TypologyRole(x[0], x[1], None, x[2]))
    
    def getAvailableRoles(self):
        return self.db.exep("SELECT typeId, roleId, name FROM roles", [], lambda x: TypologyRole(x[0], None, x[1], x[2]))
    
    async def newTypologyRole(self, role, req):
        role2 = await u.createRoleAfterRoleByName(req.bot, req.msg, role.name, discord.Colour.default(), [-1, -1, -1, "LII", -1, "so/sp", "125", "Choleric [Dominant]", "FVLE", "RCOAI"][role.systemId], doNotReposition=True)
        result = TypologyRole(role.typeId, role.systemId, role2.id, role.name)
        self.availableRoles.append(result)
        self.db.exe("INSERT INTO roles VALUES (?, ?, ?)", [role.typeId, role2.id, role.name])
        self.db.commit()
        return result
    
    async def processRequest(self, req):
        roles = req.text.split()
        invalid, toAdd, toRemove = [], [], []
        deprecated = []
        for roleName in roles: # remove 
            if re.match("\d{3}", roleName):
                deprecated.append(roleName)
                continue
            role = u.scan(self.allRoles, lambda x: re.match("(?i)^" + roleName, x.name))
            if not role:
                invalid.append(roleName)
                continue
            existingRole = scan(self.availableRoles, lambda x: x.typeId == role.typeId)
            resultRole = existingRole if existingRole else await self.newTypologyRole(role, req)
            if scan(req.author.roles, lambda x: x.id == resultRole.roleId):
                toRemove.append(resultRole.toFakeRole())
            else:
                toAdd.append(resultRole.toFakeRole())

        toRemove = set(toRemove)
        toAdd = set(toAdd)
        invalid = set(invalid)
        
        result = []
        if invalid:
            result.append(f"Invalid role(s): {', '.join(u.ts(invalid))}")
        if deprecated:
            result.append(f"Deprecated role(s) (moved to bot's profiles system): {', '.join(u.ts(deprecated))}")
        if toAdd:
            result.append(f"Given role(s): {', '.join(u.ts(toAdd))}")
            await req.author.add_roles(*toAdd)
        if toRemove:
            result.append(f"Removed role(s): {', '.join(u.ts(toRemove))}")
            await req.author.remove_roles(*toRemove)
        if result:
            await u.send(req.msg, "\n".join(result))
