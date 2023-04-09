from core.Util import Util as u
from core.Errors import *
import discord
import config as cfg
from core.CommandContext import *

class Bot(discord.Client):
    def __init__(
            self, 
            intents, 
            prefixes, 
            filters, 
            commandSystem
        ):
        self.prefixes = prefixes
        self.filters = filters
        self.commandSystem = commandSystem
        super().__init__(intents = intents)
    
    async def on_ready(self):
        print('Logged on as', self.user)
        
    async def handle_filters(self, msg):
        if msg.author.id in self.filters: # add reserved id for everyone?
            for filt in self.filters[msg.author.id]:
                if await filt(msg): return True
        return False
        
    def log(self, text, msg, *a):
        if not cfg.LOGGING_ENABLED: return
        isInDm = u.isInDMChannel(msg)
        print({
            "msg": text,
            "opt" : a,

            "t" : msg.content,
            "a" : {
                "user_friendly" : f"{msg.author.name}#{msg.author.discriminator}",
                "id" : msg.author.id
            },
            "w" : {
                "user_friendly" : "DM" if isInDm else f"{msg.channel.name} at {msg.guild.name}",
                "c" : {
                    "id" : msg.channel.id,
                    "name" : msg.channel.name,
                    "isDM" : isInDm
                },
                "guild": {
                    "id" : msg.guild.id,
                    "name" : msg.guild.name
                } if msg.guild else {}
            }
        })
        
    async def on_message(self, msg):
        if msg.author == self.user: return
        if await self.handle_filters(msg): return
        if not cfg.HANDLE_OTHER_BOTS_COMMANDS and msg.author.bot: return

        text = msg.content
        prefix = u.scan(self.prefixes, lambda p: text.startswith(p) and text[len(p)] != " ")

        if not prefix: return

        parts = text.split()
        commandname = parts[0][len(prefix) : ]

        if commandname not in self.commandSystem:
            self.log("INCORRECT_COMMAND_TYPED", msg)
            await msg.add_reaction('\u2753') # :question:
            return

        self.log("CORRECT_COMMAND_TYPED", msg)
        cmd = self.commandSystem[commandname]
        ctx = CommandContext(msg, prefix, commandname, self, cmd)
        try:
            await cmd(ctx)

        except OurException as aError:
            aError.handleFeedback(msg)

        except Exception as ex:
            await u.send(msg, u.getExceptionFullInfo())
            self.log("UNKNOWN_ERROR", msg, ex)
