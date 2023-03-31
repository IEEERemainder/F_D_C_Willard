import io
import discord
import re
from sys import exc_info
from traceback import format_exception

class Util:
    async def send(m, t):
        """Sends text with <=2000 symbols as text and tryes to upload file otherwise"""
        print("MESSAGE_SEND", "t='", m.content, "', a='", f"{m.author.name}#{m.author.discriminator}", "', c='", "DM" if isinstance(m.channel, discord.channel.DMChannel) else f"{m.channel.name} ({m.channel.id}) at {m.guild.name} ({m.guild.id})", "'")
        t = str(t)
        if len(t) <= 2000:
            await m.channel.send(t)
        else:
            await Util.sendt(m, t)

    async def sendt(msg, t, filename="file.txt"):
        """Tryes to send text as file"""
        t = str(t)
        b = bytearray(t, encoding="utf-8", errors="replace")
        await Util.sendb(msg, b, filename)

    async def fitlt(msg, size):
        """File is too large text"""
        await Util.send(msg, f"File is probably too large, {size} bytes (~ {round(size / 2 ** 20, 2)} MB with allowed size up to 8 MB). If server is boosted contact devs to update this check")
    
    async def sendb(msg, b, filename="unknown.bin"):
        size = len(b)
        if size > 8388608: # TODO: nitro privileges
        #if size > msg.channel.guild.filesize_limit:
            await Util.fitlt(msg, size)
        else: # large file will not upload (was attempting in past versions)
            with io.BytesIO(b) as fp:
                await Util.sendFile(msg, fp, filename)
    
    async def sendp(msg, p, filename="pic.png"):
        buf = io.BytesIO()
        p.savefig(buf, format='png')
        size = buf.seek(0, 2) # replace with buf.tell() ?
        if size > 8388608:
            await Util.fitlt(msg, size)
            return
        buf.seek(0)
        await Util.sendFile(msg, buf, filename)
        p.clf()
        p.close("all") # do i really need this command?
    
    async def sendFile(msg, fp, filename):
        await msg.channel.send(file=discord.File(fp, filename))
    
    def preventmentions(msg):
        return re.sub("<(@(!|&)?)(\d{18})>", "<\\1__\\3__>",re.sub("@((everyone)|(here))", "@__\\1__", msg))
    
    async def aexec(code, g, l, ctx):
        g["client"] = ctx.client # probably it's not good idea to multithreading
        g["msg"] = ctx.msg
        g["ctx"] = ctx
        code = f'''async def __ex(): ''' + ''.join(f'\n {l}' for l in code.split('\n'))
        print(code)
        f = exec(code
        , g, l) # TODO: fix triple quote strings issue (special way of adding tabs based on belonging to the string)
        return await l['__ex']()
    
    def scan(src, func):
        return next((x for x in src if func(x)), 0)
    
    def ts(sq):
        return (str(x) for x in sq)
    
    def getExceptionFullInfo():
        etype, value, tb = exc_info()
        info, error = format_exception(etype, value, tb)[-2:]
        return f'Exception in:\n{info}\n{error}'
    
    async def createRole(msg, roleName, roleColor=discord.Color(0)):
        return await msg.channel.guild.create_role(name = roleName, colour = roleColor)
    
    def parseArgs(c):
        c.replace(r'\"', "\0")
        #c.replace(r"\'", '\x01')
        c.replace("\\\\", '\x02')
        #((?:'[^']+[^\\]')|
        args=[x.strip("'\"").replace("\0", '"').replace('\x01', "'").replace('\x02', "\\") for x in re.findall(r"((?:\"[^\"]+[^\\]\")|(?:\S+))",c)]
        return args
    
    def processMatches(m, projector):
        if m: 
            if len(m) == 1: return m[0]
            raise MultipleMatchException(m, projector)
    
    def parseUser(s, ctx):
        if m := re.match(".*#\d{4}", s):
            return Util.scan(ctx.guild.members, lambda x: x.name == m[1].strip() and x.discriminator == int(m[2]))
        if m := re.match("(?:<@!?)?(\d{16})>?", s):
            return Util.scan(ctx.guild.members, lambda x: x.id == int(m[1]))
        projectUser=lambda x: f"{x.nick or x.name}#{x.discriminator} [{x.id}]"           
        return parseBase(s, ctx, ctx.guild.roles, projectRole, [lambda x: x.name, lambda x: x.nick])
        
    def parseRole(s, ctx):
        if m := re.match("(?:<@&)?(\d{16})>?", s):
            return Util.scan(ctx.guild.roles, lambda x: x.id == int(m[1]))
        projectRole=lambda x: f"{x.name} [{x.id}]"
        return parseBase(s, ctx, ctx.guild.roles, projectRole, [lambda x: x.name])
        
    def parseChannel(s, ctx):
        if m := re.match("(?:<#)?(\d{16})>?", s):
            return Util.scan(ctx.guild.channels, lambda x: x.id == int(m[1]))
        projectChannel=lambda x: f"{x.name} [{x.id}]"
        return parseBase(s, ctx, ctx.guild.channels, projectChannel, [lambda x: x.name])
        
    def parseBase(s, ctx, col, projector, propertyFns):
        processBaseStage(s, ctx, col, projector, propertyFns, lambda x: x == s)
        s2 = s.casefold()
        processBaseStage(s, ctx, col, projector, propertyFns, lambda x: x.casefold() == s2)
        processBaseStage(s, ctx, col, projector, propertyFns, lambda x: x.startswith(s))
        processBaseStage(s, ctx, col, projector, propertyFns, lambda x: x.casefold().startswith(s2))
        return None
    
    def processBaseStage(s, ctx, col, projector, propertyFn, checkFn):
        matches = [x for x in col if all([checkFn(propertyFn(x)) for propertyFn in propertyFns])]
        if ret := processMatches(matches, projector): return ret

    def isInDMChannel(m): return isinstance(m.channel, discord.channel.DMChannel)
