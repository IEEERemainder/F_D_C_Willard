from Filters import *
from core.Constraint import * 
from core.CommandSystem import *
from core.Command import *
from core.Bot import *
from core.IdStorage import *
from Commands import *
import discord
import config as cfg

noDmCons = Constraint(extraFunc = u.isInDMChannel)
rolesFn = lambda m: [role.id for role in m.author.roles]
idFn = lambda m: m.author.id
guildFn = lambda m: m.channel.guild.id
exampleOnlyToRolesCons = Constraint(only = [ids.role("КрекерОповещение")], func = rolesFn)
exampleBanRolesCons = Constraint(banned = [ids.role("КрекерОповещение")], func = rolesFn)
exampleOnlyToGuilds = Constraint(only = [ids.guild("КтоЭтиВашиТипыИчности")], func = guildFn)

filters = {
    ids.user("Крекер"): [ControlledMentionFilter("&announcement", ids.role("КрекерОповещение"))],
    ids.user("ego"): [ControlledMentionFilter("&testrole", ids.role("ТестированиеРеагированияБотаНаСообщениеСПсевдоупоминанием"))], 
    ids.user("Крабик"): [
        DeleteOnClueFilter("https://tenor.com/view"), 
        DeleteOnRegexFilter(".*долб.{2}б.*")
    ]
}

onlyToEgo = Constraint(only = [ids.user("ego")], func = idFn)

#pDBGraphsCommandsSystem = PDBGraphsCommandsSystem()

commandSystem = CommandSystem(
    Command(evalc, "!", onlyToEgo),
    Command(evalAndRespC, "/", onlyToEgo),
    #Command(v, "v"),
    #Command(restartV, "rv",onlyToEgo),
    #Command(jseval, "js"),
    #Command(pDBGraphsCommandsSystem.enneagraphs, "egs"),
    #Command(pDBGraphsCommandsSystem.mbtigraphs, "mgs"),
    #Command(pDBGraphsCommandsSystem.enneagraph, "eg"),
    #Command(pDBGraphsCommandsSystem.mbtigraph, "mg"),
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = Bot(intents, ["!"], filters, commandSystem)

with open(cfg.TOKEN_FILE_PATH) as f:
    token = f.read()

client.run(token)

del token
