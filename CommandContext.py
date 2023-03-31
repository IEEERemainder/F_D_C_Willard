import io
from Util import Util as u

class CommandContext:
    def __init__(self, msg, prefix, cmd, client, commandObj):
        self.msg = msg
        self.channel = msg.channel
        self.guild = self.channel.guild
        self.prefix=prefix
        self.cmdName=cmd
        self.client=client
        self.command
        self.t = msg.content[len(prefix)+len(self.cmdName)+1:].strip() # prefix commandName space
        self.args=[]
        self.parseArgs()
        self.argc = len(self.args)

    async def send(self, what, **kwgs):
        kwgs = __KwgsHelper(kwgs)
        if isinstance(what, io.IOBase): # file
            await u.sendFile(self.msg, what, kwgs.nz('filename', 'unknown.bin'))
        elif isinstance(what, str):
            wrap = kwgs.nz('wrap', -1)
            asFile = kwgs.nz('asFile', False)
            text = what
            if wrap != -1:
                text = '\n'.join(textwrap.wrap(
                    text, 
                    width = wrap, 
                    replace_whitespace = kwgs.nz('replaceWhitespace', False)
                ))
            if asFile:
                await u.sendt(self.msg, text, kwgs.nz('filename', 'file.txt'))
            else:
                await u.send(self.msg, text)
        elif type(what).__name__ == "module" and what.__name__ == 'matplotlib.pyplot': # plt
            await u.sendp(self.msg, what)

    def parseArgs(self):
        self.args = u.parseArgs(self.t)

    def __getitem__(self, index):
        return ConversionsIntermediary(self.args[index], self)

# more than 1 class in file?

class ConversionsIntermediary:
    def __init__(self, t, ctx):
        self.ctx = ctx
        self.t = t

    def i(self): return int(self.t)

    def f(self): return float(self.t)

    def user(self): return u.parseUser(self.t, self.ctx)

    def role(self): return u.parseRole(self.t, self.ctx)

    def channel(self): return u.parseChannel(self.t, self.ctx)

    def a(self, fn=int, delimiter=','): return [fn(x) for x in self.t.split(delimiter)]
            
class __KwgsHelper(dict):
    def nz(self, key, defaultValue):
        return self[key] if key in self 
            else defaultValue