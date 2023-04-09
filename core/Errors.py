class OurException(Exception):
    def __init__(self, msg="", reaction="", logMessage="UNKNOWN"):
        self.msg = msg
        self.reaction = reaction
        self.logMessage = logMessage
        self.log = logMessage != "NO_LOG"
        super().__init__()

    async def handleFeedback(self, msg):
        if self.msg:
            await u.send(msg, self.msg)
        if self.reaction:
            await msg.add_reaction(self.reaction)
        if LOGGING_ENABLED and self.log:
            client.log(self.logMessage, msg)

class AccessError(OurException):
    def __init__(self, msg=""):
        super().__init__(msg, "\U0001f6ab", "ACCESS_DENIED") # :no_entry_sign:

class InternalError(OurException):
    def __init__(self, msg=""):
        super().__init__(msg,  "\u274C", "INTERNAL_ERROR") # :x:

class MultipleMatchException(OurException):
    def __init__(self, a, fn):
        nl = '\n'
        super().__init__(f"More than one match found:{nl + nl.join([fn(x) for x in a])}", "", "NO_LOG")
