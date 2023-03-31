from Filters import *
from Constraint import * 
from CommandSystem import *
from Command import *
from Bot import *
from IdStorage import *
from Commands import *
import discord

LOGGING_ENABLED = True
HANDLE_OTHER_BOTS_COMMANDS = False
TOKEN_FILE_PATH = "~/discord_bot/FDCWillard.toc"
PDBGRAPHS_DB_PATH = "/media/paul/B0701CFA701CC94C/Users/Paul/root/db/proj1612_2.db"
DATABASECMDS_DB_PATH = "/media/paul/B0701CFA701CC94C/Users/Paul/root/db/proj1612_1.3.26.db"
VC_CHECED_IDS_DB_PATH = "/media/paul/B0701CFA701CC94C/Users/Paul/root/db/cnownVcIds.db"
CHROMIUM_SESSIONS_TEMPPATH = "~/discord_bot/temp"
EMPTY_HTML_URL = 'file:///home/paul/discord_bot/emptyhtml/empty.html'
VC_DISALLOWED_IDS = [ "150488654", "497920655", "493104482", "503859211", "45916594", "148374060", "377721107", "152355743", "41833069", "292394301", "574658359", "263245347", "180600558", "148330788", "369965243", "25647977", "736212984", "17811718", "10199925", "144723155", "335947101", "339629167", "137243563", "179022270", "168532782", "753092295", "258275177", "277831073", "161087088", "271669076", "484074682", "126647826", "600637824", "141856074", "151806707", "622059335", "203730137", "292029106", "223926597", "336861357", "369341789", "221277910", "341218859", "252916518", "450166640", "574278536", "240495438", "190384965", "561313387", "492915280", "3778835", "14577372", "25249847", "29847967", "35385977", "42376947", "56646786", "60809171", "95074574", "122733794", "123499156", "127812828", "131706504", "140652553", "141514324", "153013890", "163990070", "165606488", "165855269", "168283110", "172181560", "177415413", "179548501", "183358219", "183514553", "187557416", "201219027", "202439940", "206352149", "213349854", "216232048", "223774852", "225068826", "225248386", "229936220", "232624733", "234738505", "237710389", "239067066", "239225018", "243571841", "247716291", "248373583", "249213856", "250323665", "252501669", "257290739", "259709464", "261376501", "268617850", "270583136", "272255522", "273085343", "275220327", "277295758", "278883419", "279893349", "280860252", "283775132", "283996079", "284775046", "289148180", "293517073", "293752516", "297229046", "299287014", "299427699", "302066520", "302069131", "306534040", "310228209", "310696937", "310784072", "316771823", "316857330", "317534339", "317926606", "319746637", "320331329", "322071737", "322750673", "324013111", "324773613", "325892954", "326771731", "328227520", "329790651", "333004699", "333102677", "335955851", "337743514", "337922851", "338325246", "338329671", "339073893", "339127088", "339132687", "339194257", "339285636", "339505663", "339514567", "339651295", "340402171", "340433670", "340489788", "340765108", "341127806", "341590125", "343353389", "343692742", "344404105", "346127259", "347361669", "347824224", "347831831", "348014013", "349202874", "349345361", "350624955", "350712224", "350903730", "351125675", "352754204", "353911584", "361060317", "361806369", "364175766", "369270343", "373899542", "381178417", "381320269", "388728626", "390208562", "394910373", "398702553", "399837935", "404755597", "407271492", "410337981", "410394699", "413327449", "416815100", "431374734", "434217278", "435805416", "437538528", "438622416", "438933917", "439166225", "442388261", "444901214", "446681792", "446743282", "446857941", "453481275", "454325035", "455213868", "457296789", "463914950", "473184971", "475478143", "487090940", "487824109", "488374905", "492932442", "505823547", "518868288", "529294750", "530418132", "539450777", "549785698", "551513959", "565614986", "571645303", "572956556", "579765118", "589597714", "595391079", "617514006", "653040495", "664332494", "terraz" ]

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

pDBGraphsCommandsSystem = PDBGraphsCommandsSystem()

commandSystem = CommandSystem(
    Command(evalc, "!", onlyToEgo),
    Command(evalAndRespC, "/", onlyToEgo),
    Command(v, "v"),
    Command(restartV, "rv",onlyToEgo),
    #Command(jseval, "js"),
    Command(pDBGraphsCommandsSystem.enneagraphs, "egs"),
    Command(pDBGraphsCommandsSystem.mbtigraphs, "mgs"),
    Command(pDBGraphsCommandsSystem.enneagraph, "eg"),
    Command(pDBGraphsCommandsSystem.mbtigraph, "mg"),
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = Bot(intents, ["!"], filters, commandSystem)

with open(TOKEN_FILE_PATH) as f:
    token = f.read()

client.run(token)

del token
