import re
from core.Util import Util as u

class ControlledMentionFilter:
    def __init__(self, clue, roleId):
        self.clue = clue
        self.roleId = roleId

    async def __call__(self, msg):
        if self.clue in msg.content:
            await u.send(msg, f"<@&{roleId}>")
            return True
        return False

class DeleteOnClueFilter:
    def __init__(self, clue):
        self.clue = clue

    async def __call__(self, msg):
        if self.clue in msg.content:
            await msg.delete()
            return True
        return False
        
class DeleteOnRegexFilter:
    def __init__(self, regex):
        self.regex = regex

    async def __call__(self, msg):
        if re.match(self.regex, msg.content):
            await msg.delete()
            return True
        return False

class TestDeleteOnClueFilter:
    def __init__(self, clue):
        self.clue = clue
        
    async def __call__(self, msg):
        if self.clue in msg.content:
            await msg.add_reaction("🗑️")
            return True
        return False
