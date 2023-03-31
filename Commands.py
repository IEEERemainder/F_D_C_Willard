import aiohttp, asyncio, datetime, discord, inspect, io, itertools, json, math, matplotlib.pyplot as plt, random, re, requests, sqlite3, textwrap, time, libretranslate
from ChromiumWrapperNew import ChromiumWrapperNew
from Errors import *
from SQLiteWrapper import SQLiteWrapper
from TypesStorage import TypesStorage
from Util import Util as u
from sys import exc_info
from traceback import format_exception
from urllib import parse
from yarl import URL
from zipfile import ZipFile

async def evalc(ctx):
    """Allows devs to execute arbitrary code"""
    await u.aexec(ctx.t, globals(), locals(), ctx) 

async def evalAndRespC(ctx):
    await ctx.send(await u.aexec(ctx.t, globals(), locals(), ctx))

# probably split to files?

class PDBGraphsCommandsSystem:
    def __init__(self):
        self.db = SQLiteWrapper(PDBGRAPHS_DB_PATH)
    
    async def graphsb(self, msg, rows, cols, sizeX, sizeY, left, right, bottom, top, wspace, hspace, xTypes, subplotTypes, func):
        figure, axis = plt.subplots(rows, cols, figsize=(sizeX, sizeY))
        plt.subplots_adjust(left = left, right = right, bottom = bottom, top = top, wspace=wspace,hspace=hspace)
        # defaults are - left  = 0.125 right = top = 0.9 bottom = 0.1 wspace = hspace = 0.2
        def f(where, subplotType, xTypes_, ys):
            xs = range(len(xTypes_))
            where.bar(xs, height=ys)
            where.set_xticks(xs, minor=False)
            where.set_xticklabels(xTypes_, fontdict=None, minor=False, rotation=90)
            where.set_title(subplotType)
            where.set_ylim(top=where.get_ylim()[1] * (1 + 1 / 6)) # space for data labels
            for (x, y) in zip(xs,ys):
                where.text(x, y, str(y), rotation=90, wrap=True)
        for i in range(len(subplotTypes)):
            f(axis[i // cols, i % cols], subplotTypes[i], xTypes, func(subplotTypes[i], xTypes))
        await u.sendp(msg, plt)

    async def graphb(self, msg, xs, ys, labels):
        plt.figure(figsize=(8, 6), dpi=80)
        plt.bar(xs, height=ys)
        plt.xticks(xs, labels)
        for (x, y) in zip(xs,ys):
            plt.text(x, y, str(y), rotation=90, wrap=True)
        await u.sendp(msg, plt)

    async def xgraphs(self, ctx, rows, cols, types1, types2, func):
        await self.graphsb(ctx.msg, # TODO: derive formula to calculate height and width from len(data[dimension])
            rows, cols, 
            18, 15, 
            0.05, 0.95,
            0.05, 0.95,
            0.3, 0.3,
            types1,
            types2,
            func
        )
    
    async def enneagraphs(self, ctx):
        await self.xgraphs(ctx, 4, 4, TypesStorage.mbti(), TypesStorage.enneagram(), lambda subplotType, xTypes: [self.db.onlyInt("SELECT SUM(count) FROM partialProfiles WHERE personality LIKE ?", [f'{xType} {subplotType}']) for xTypes in xTypes])

    async def mbtigraphs(self, ctx):
        await self.xgraphs(ctx, 5, 4, TypesStorage.enneagram(), TypesStorage.mbti(), lambda subplotType, xTypes: [self.db.onlyInt("SELECT SUM(count) FROM partialProfiles WHERE personality LIKE ?", [f'{subplotType} {xType}']) for xTypes in xTypes])
    
    async def mbtigraph(self, ctx):
        ennea = ctx.t
        mbti = TypesStorage.mbti()
        await self.graphb(ctx.msg, range(16), [self.db.onlyInt("SELECT SUM(count) FROM partialProfilesTypesCounts WHERE personality LIKE ?", [f'{m} {ennea}']) for m in mbti], mbti)

    async def enneagraph(self, ctx):
        mbti = ctx.t
        ennea = TypesStorage.enneagram()
        await self.graphb(ctx.msg, range(18), [self.db.onlyInt("SELECT SUM(count) FROM partialProfilesTypesCounts WHERE personality LIKE ?", [f'{mbti} {e}']) for e in ennea], ennea)

class DatabaseCommands:
    def __init__(self):
        self.db = SQLiteWrapper(DATABASECMDS_DB_PATH, True)
        self.MAX_LINES_FOR_PLAIN_TEXT = 15

    async def handleResults(self, r):
        await ctx.send("no results" if len(r) == 0 else "\n".join(["; ".join(u.ts(x)) for x in r]), asFile = len(r) > self.MAX_LINES_FOR_PLAIN_TEXT)

    async def queryPdbc(self,ctx):
        await self.handleResults(self.db.exefns(lambda x: x.fetchall(), ctx.t))  

    async def pdbcsb(self, q, ctx):
        await self.handleResults(self.db.all(f"SELECT p.id, p.name, personality, c.name, s.name, votes || '/' || comments FROM partialProfiles AS p INNER JOIN subcategories AS s ON p.subCatId = s.id INNER JOIN categories AS c ON c.id = p.catId WHERE {q} LIKE ?", [ctx.t])) # rewrite probably. As long as q is not freely accessible SQL injection is impossible

    async def pdbcst(self,ctx):
        await self.pdbcsb("personality", ctx)

    async def pdbcsn(self,ctx):
        await self.pdbcsb("partialProfiles.name", ctx)

    async def pdbcss(self,ctx):
        await self.pdbcsb("subcategories.name", ctx)    

    async def simplewhere(self, ctx):
        ctx.t = """SELECT p.id
, p.name
, t1.type AS mbti
, t2.type AS enneagram
, t3.type AS socionics
, t4.type AS instinctualVariant
, t5.type AS tritype
, t6.type AS temperaments
, t7.type AS attitudinalPsyche
, t8.type AS big5
, s.subcategory AS subcategory
, votes
, comments 
FROM partialProfilesOptimized p 
INNER JOIN subcategories s ON s.id = subcatId
INNER JOIN categories c on c.id = s.catId
INNER JOIN types t1 ON t1.id = mbti_ 
INNER JOIN types t2 ON t2.id = ennea_ 
INNER JOIN types t3 ON t3.id = soc_ 
INNER JOIN types t4 ON t4.id = inst_ 
INNER JOIN types t5 ON t5.id = tritype_ 
INNER JOIN types t6 ON t6.id = temper_ 
INNER JOIN types t7 ON t7.id = att_ 
INNER JOIN types t8 ON t8.id = p.big5_ WHERE """ + ctx.t # should probably implement mechanism for aliases, this one depend on concrete alias logic
        await self.queryPdbc(ctx)   

class OnlyVkComUsersAndGroupsExceptSpecifiedGuard:
    def __init__(self, disallowIds): # ids for specified chec euristics - number for user and club + number or id for id
        self.disallowIds = disallowIds
        self.db=SQLiteWrapper(VC_CHECED_IDS_DB_PATH)
        self.lastQueryApproved=""

    def check(self, query):
        prefix="https://vk.com/"
        if not query.startswith(prefix): raise AccessError("Only https://vk.com/* allowed")
        if query==self.lastQueryApproved: return
        query = query[len(prefix):]
        if query.startswith("search?c"): 
            self.lastQueryApproved=query
            return
        if '?' in query: # for security reasons, users so far didn't use params after ? except search TODO
            query = query[:query.find('?')]
        if self.checTrivial(query):
            self.lastQueryApproved=query 
            return
        if self.checIfAlreadyBeenValidated(query):
            self.lastQueryApproved=query 
            return

        vcinfo = self.vcrinfo(query)

        if vcinfo==0 or self.isgroup(query):
            self.vcexist.exe("INSERT INTO cnownIds VALUES (?)", [query])
            self.db.commit()
            self.lastQueryApproved=query
            return

        if vcinfo == 3:
            raise AccessError("Neither a search request or user or group page id")
        elif vcinfo == 2:
            raise AccessError("Friend's page. Contact if no data is exposed or friend don't mind it")
        else:
            raise AccessError("Owner's page")

    def isgroup(i):
        g = requests.get(f"https://list-vk.com/group/{i}/")
        return g.url != "https://list-vk.com/"

    def vcinfo(self, i): # fix number codes TODO
        url= requests.get(f"https://list-vk.com/{i}/").url 
        if url=="https://list-vk.com/339442125/": return 4
        if url == "https://list-vk.com/": return 3
        digits = re.findall("(\d+)", url)[0]
        if digits in self.disallowIds: return 2 # groups and users has different id systems? BUG
        return 0

    def checTrivial(self, q):
        return str(q) in self.disallowIds 
            or (re.match("^id\d+$",q) and q[2:] not in self.disallowIds) 
            or re.match("^public\d+$",q) 
            or re.match("^club\d+$",q) 

    def checIfAlreadyBeenValidated(q):
        return self.db.exe("SELECT * FROM cnownIds WHERE id= ?",[q]).fetchone()

class ChromiumCommand:
    def __init__(self, fn, names, signature, info=None, byDefault=False, restricted=False):
        self.fn = fn
        self.names = names
        self.decoration = '__' if byDefault else '**'
        self.signature = signature
        self.info = info
        self.restricted = restricted

    def __str__(self):
        globalDecoration='~~' if self.restricted else ''
        return f"{globalDecoration}{'/'.join([self.decoration + name + self.decoration for name in self.names])}({self.signature}){self.info and ' (' + self.info + ')' or ''}{globalDecoration}"

    def parseArgs(self, argsS):
        parts = self.smartSplitByComma(argsS)
        args = {}
        signatureData = list(self.signature.cwgs.items())
        for i in range(parts):
            p = parts[i]
            if p[2]:
                parts2 = p.split('=', 1) # there may be = in value, but since argName is always valid js identifier it should not contain = (however doesn't exclude all potentially leading to misfuncion cases by user fantasy)
                cey = p[0].strip()
                value = p[1].strip().strip("'") # ceep spaces within string
            else:
                cey = signatureData[i][0]
                value = p
            args[cey] = signatureData[i][1](value)
        args = {**args, sd[0] : sd[1].strip("'") for sd in signatureData if sd[0] not in args} # add args those values was not supplied
        return args
            
    def smartSplitByComma(self, t):
        t += ','  # to omit final step in automaton. yeah regex is simplier but discrete mathematics is powerful tool to those who has pal up with it (not yet for me)

        inString, named, escapedPos, startPos, endPos, = False, False, -1, 0, -1 # state
        result=[]

        for i in range(len(t)):
            c = t[i]
            if c == '\\':
                escapedPos = i+1

            if c == '=' and not inString:
                named = True

            if c == "'" and not i == escapedPos:
                if inString:
                    endPos = i
                inString = not inString

            if c == ',' and not inString:# capture
                if endPos > startPos:
                    v=t[startPos:endPos+1].strip()
                    if not named:
                        v=v[1:-1]
                    result.append((v, 'str',named))
                else:
                    result.append((t[startPos:i].strip(), 'notstr',named))
                startPos = i+1
                named = False
        return result

class ChromiumCommandsSession:
    def __init__(self, chromiumWrapper, ctx):
        self.tempPath = CHROMIUM_SESSIONS_TEMPPATH
        self.chr = chromiumWrapper
        self.scipList = []
        self.ctx = ctx

    async def updateScipList(self, *els):
        self.scipList.extend(els)
        self.scipListSelector = ",".join(self.scipList) # TODO: Add (s1),(s2)?

    async def querySelector(self, qs):
        return await self.chr.page.JJ(f"{qs}:not({self.scipListSelector}")

    async def handleScipList_Init(self):
        await self.chr.exe("var d_d_q_storageForTempEditedThings = []; var d_d_q_currentIndex = 0; ") # chec if there are already vars with specified names? TODO

    async def handleScipList_DeepHide(self, el):
        await el.JJeval(self.scipListSelector, """(nodes => nodes.forEach(function(x) {
            let atts = Array.from(x.attributes, x => {'name':x.name, 'value':x.value});
            let obj = {'el': x, 'html':x.innerHTML, 'atts': atts};
            x.innerHTML = ''; 
            for (let v of atts) {
                x.attributes.removeNamedItem(v[0]); 
            } 
            d_d_q_storageForTempEditedThings[d_d_q_currentIndex] = obj; 
            d_d_q_currentIndex++; 
        }))""")

    async def handleScipList_Revert(self):
        await self.chr.exe("""for (let i = 0; i < d_d_q_currentIndex; i++) {
            let e = d_d_q_storageForTempEditedThings[i]; 
            e.el.innerHTML = e.html; 
            for (let att in e.atts) { 
                const node = document.createAttribute(att.name); 
                node.value = att.value; 
                e.el.attributes.setNamedItem(node); 
            } 
        }""")

    async def selectorCommandsCommonLogic(self, args, fn, state):
        await self.handleScipList_Init()
        for el in self.querySelector(args["selector"]):
            await self.handleScipList_DeepHide(el, state)
            await self.fn(el)
        await self.handleScipList_Revert()

    async def screenshotFn(self, args):
        state = {"index": 0, "invisible": 0}
        
        async def screenshotFnLogic(self, el, state):
            if not await el.boundingBox():
                state["invisible"] += 1
                continue
            await el.screenshot({
                "captureBeyondViewport":True,
                "fromSurface":True, 
                "path":os.path.join(self.tempPath, f"img{state['index']}.png")
            })
            state['index'] += 1

        await self.selectorCommandsCommonLogic(args, screenshotFnLogic, state)

        MAX_IMAGES_TO_BE_SENT_BY_10_IMGS_PER_MESSAGE = 30

        if state['index'] > MAX_IMAGES_TO_BE_SENT_BY_10_IMGS_PER_MESSAGE: # too many?
            zipPath = os.path.join(self.tempPath, 'archieved.zip')
            with ZipFile(zipPath, 'w') as zipObj:
                for i in range(state['index']):
                    zipObj.write(f"img{i}.png")
                await ctx.send(open(zipPath), filename="archieved.zip")
            return

        imagesIds = list(range(state['index']))
        # 10 files max per message

        while imagesIds:
            files = [discord.File(os.path.join(self.tempPath, f"img{x}.png")) for x in imagesIds[:10]]
            await ctx.msg.channel.send(files=files)
            del imagesIds[:10]

        INVISIBLE_ELS_NOTIFY = False
            
        if state['invisible'] and INVISIBLE_ELS_NOTIFY:
            await msg.channel.send(f"{state['invisible']} elements was hidden")

    async def textFn(self, args):
        state = {"result": []}

        async def textFnLogic(self, el, state):
            t = await el.JJeval('*', "(nodes => nodes.map(n => n.innerText))")[0]
            if t:
                state["result"].append(t)

        await self.selectorCommandsCommonLogic(args, textFnLogic, state)
        d = state["result"]
        if args["target"] != "":
            d = self.translate(d, args["source"], args["target"])
        await self.ctx.send("\n\n".join(d), wrap=args["width"], asFile = args["asfile"])

    async def translate(self, d, src, dst):
        return [await libretranslate.translate("http://localhost:5000", x, src, dst) for x in d]
        
    async def htmlFn(args,sciplist,msg):
        state = {"result": []}

        async def htmlFnLogic(self, el, state):
            t = await el.JJeval('*', "(nodes => nodes.map(n => n.innerHTML))")[0]
            if t:
                state["result"].append(t)

        await self.selectorCommandsCommonLogic(args, htmlFnLogic, state)

        await self.ctx.send("\n\n".join(state["result"]), wrap=args["width"])

    async def removeFn(args,sciplist,msg):
        await chr.page.JJeval(args[0], '(nodes => nodes.map(el => el.parentElement.removeChild(el)))')

    async def scrollFn(args,args):
        await chr.exe("""
            function sleep_(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
            async function scroll_(dx, dy = 0, n = 1, d = 0) {
                if (n < 0) throw Error('negative n');
                if (d < 0) throw Error('negative d'); 
                for (var i = 0; i < n; i++) { 
                    window.scrollBy(dx, dy); 
                    await sleep_(d); 
                }
            }
            await scroll_(""" + 
            ",".join([x for x in args.values() if not [c for c in x if c in "-0123456789"]]) + # standartize isInt checs... TODO
            ");"
        )

    async def waitForSelectorFn(args,args):
        await chr.page.waitForSelector(args['selector'])

    async def setviewpointFn(self, args):
        # do we need to execute it if page dont reload lol\
        args["height"] = await chr.exe('Math.ceil(document.body.getBoundingClientRect().height)') if args["height"] == 'bodyHeight' 
        await chr.page.setViewport(args)

    async def scipFn(self, args):
        await self.updateScipList(args['selector'])

    async def hideFn(self, args):
        await chr.page.JJeval(args['selector'], '(nodes => nodes.map(el => el.style[\'display\']="none"))')

    async def clickFn(self, args):
        raise InternalError("restricted function 'click'") # for security reasons, since I'm logged in vk.com and this functionality is limited to it, however, that's not the only case

    async def pressFn(self, args):
        raise InternalError("restricted function 'press'")

    async def typeFn(self, args):
        raise InternalError("restricted function 'type'")

    async def evalFn(self, args):
        raise InternalError("restricted function 'eval'")

    async def removeAllButWorkspaceFn(self, args):
        await chr.page.waitForSelector('#fastchat-reforged, #page_header_cont, #side_bar, #stl_left, .group_friends, .people_module')
        await chr.exe("for (el of document.querySelectorAll('#fastchat-reforged, #page_header_cont, #side_bar, #stl_left, .group_friends, .people_module')) el.parentElement.removeChild(el);")

    async def expandPostsTextFn(self, args):
        await chr.exe("for (el of document.querySelectorAll('.PostTextMore__content')) el.click();")

    async def skipScriptsFn(self, args):
        await self.updateScipList('script')

class ChromiumCommandSignature:
    def __init__(self, **cwgs):
        self.cwgs = cwgs

    def __str__(self):
        return ', '.join(['`' + c + '`:' + self.cwgs[c][0].__name__ + (self.cwgs[c][1] and '=' + str(self.cwgs[c][1]) or '') for c in self.cwgs])

class ChromiumScheduler:
    def __init__(self):
        self.lastQuery=''
        pass

    def goto(self, url):
        if url == self.lastQuery: return
        await self.chr.goto(url)
        self.lastQuery = url
        if (self.chr.page.url).startswith("https://vk.com/blank.php?"):
            raise InternalError("blank page")

class ChromiumSupportCommandSystem: 
    def __init__(self):
        self.chr = ChromiumWrapperNew()
        self.launched = False
        self.lasturlpart=None
        self.vReady = True
        self.saveQLoaded=False
        self.scheduler = ChromiumScheduler()
        self.securityGuard = OnlyVkComUsersAndGroupsExceptSpecifiedGuard(VC_DISALLOWED_IDS) # my friends and group there I'm administrator
        
        def ourParseBool(self, x):
            return x in ["1", 1, "true", True]
            
        ourParseBoolF = ourParseBool
        ourParseBoolF.__name__ = "bool" # rename so that str(signature) return correct type hint

        #async def ourParseHeight(self, x):
        #    return await self.chr.exe('Math.ceil(document.body.getBoundingClientRect().height)') if x == 'bodyHeight' else int(x)
        #ourParseHeightF = ourParseHeight
        #ourParseHeightF.__name__ = 'int'
        # should be executed after previous commands as they can change page layout

        self.commands = [
            ChromiumCommand(
                ChromiumCommands.screenshotFn,
                ["screenshot", "s"], 
                ChromiumCommandSignature(selector=[str, "'body'"])
            ),
            ChromiumCommand(
                ChromiumCommands.textFn,
                ["text", "t"], 
                ChromiumCommandSignature(
                    selector=[str, "'body'"], 
                    width=[int, -1], 
                    target=[str, "''"], 
                    source=[str, "'auto'"], 
                    asfile=[ourParseBoolF, 1]
                )
            ),
            ChromiumCommand(
                ChromiumCommands.htmlFn, 
                ["html", "h"], 
                ChromiumCommandSignature(
                    selector=[str, "'body'"], 
                    width=[int, -1], 
                    asfile=[ourParseBoolF, 1]
                )
            ), # я устал. Можно конечно linter настроить но как-то да
            ChromiumCommand(ChromiumCommands.removeFn, ["remove", "r"], ChromiumCommandSignature(selector=[str, None])),
            ChromiumCommand(ChromiumCommands.hideFn, ["hide", "d"], ChromiumCommandSignature(selector=[str, None])),
            ChromiumCommand(ChromiumCommands.screenshotFn, ["screenshot", "s"], ChromiumCommandSignature(selector=[str, "'body'"])),
            ChromiumCommand(ChromiumCommands.clickFn, ["click", "c"], ChromiumCommandSignature(selector=[str, "'body'"], conf=[str, "'left(0,0);'"]), "currently restricted (primary key, down+up, other confs in eval (as well as **press**))", restricted=True),
            ChromiumCommand(ChromiumCommands.pressFn, ["press", "p"], ChromiumCommandSignature(selector=[str, "'body'"], conf=[str, None]), "same", restricted=True),
            ChromiumCommand(ChromiumCommands.typeFn, ["type", "y"], ChromiumCommandSignature(selector=[str, "'body'"], text=[str, None]), "same", restricted=True),
            ChromiumCommand(ChromiumCommands.evalFn, ["eval", "e"], ChromiumCommandSignature(js=[str, None]), "are you kidding?", restricted=True),
            ChromiumCommand(ChromiumCommands.skipFn, ["skip", "k"], ChromiumCommandSignature(selector=[str, None]), "there are :not, lol"),
            ChromiumCommand(scrollFn, ["scroll", "l"], ChromiumCommandSignature(dx=[int, None], dy=[int, 0], times=[int, 1], delayMs=[int, 0]), "combine with **waitforselector** or replace with action('selector:nth-child(-n + COUNT)', ...);remove('selector:nth-child(-n + COUNT)')"),
            ChromiumCommand(ChromiumCommands.waitForSelectorFn, ["waitforselector", "w"], ChromiumCommandSignature(selector=[str, None])),
            ChromiumCommand(ChromiumCommands.setviewpointFn, ["setviewpoint", "v"], ChromiumCommandSignature(width=[int,None], heigth=[str, None], deviceScaleFactor=[float, 1.0], isMobile=[ourParseBoolF, 0], hasTouch=[ourParseBoolF, 0], isLandscape=[ourParseBoolF, 0]), "bodyHeight for out-of-screen content render (in some cases). So `heigth` is either the string `bodyHeight` or a heigth in pixels"),

            ChromiumCommand(ChromiumCommands.removeAllButWorkspaceFn, ["removeAllButWorkspace"], "", "remove('#fastchat-reforged, #page_header_cont, #side_bar, #stl_left, .group_friends, .people_module')", byDefault=True),
            ChromiumCommand(ChromiumCommands.expandPostsTextFn, ["expandPostsText"], "", "click('.PostTextMore\\_\\_content')", byDefault=True),
            ChromiumCommand(ChromiumCommands.skipScriptsFn, ["skipScripts"], "", "skip('script')", byDefault=True),
        ]
        self.helpLines = [
            #"Invalid syntax. Valid is",
            "!v `urlpart` `actions`",
            "Page address is 'https://vk.com/' + `urlpart`, should be user or group page or 'search?...'. If the same as in previous command use, don't reload page (for dynamic pages)",
            "`actions` is semicolon-separated list of build-in functions (use ' ' for str args) (by default funcs are marked __underline__)",
            "If argument contains spaces, delimit it by \" \". If argument should contain \", or \\ place \\ in front of them (\\\\\", \\\\\\\\).",
            "Available build-in functions: ",
        ]

    async def checkLaunched(self):
        if not self.launched:
            await self.chr.launch()
            self.launched=True

    async def checkReady(self):
        if not self.ready: # quite poor sync mechanism
            raise InternalError("Command in progress") # add current cmd to queue?

    def parseCommands(self, argsS): # parseArgs calls parseArgs, clarify semantics TODO
        parts = argsS.split(';') # may there be a ; within action ? TODO?
        result = []
        for part in parts:
            v = part.strip()
            openingBraceIndex = v.find('(')
            if openingBraceIndex == -1 or v[-1] != ')':
                raise InternalError(f"Unable to process action '{v}', did you enclose params in () (even if there are none)?")
            fnName = v[:openingBraceIndex]
            cmd = u.scan(self.commands, lambda x: fnName in x.names)
            if not cmd:
                 raise InternalError(f"unknown command '{fnName}'")
            if cmd.restricted:
                raise InternalError(f"Restricted command '{fnName}'")
            result.append((cmd, cmd.parseArgs(v[openingBraceIndex+1:-1])))

    async def v(self, ctx):
        if ctx.argc == 1 and ctx[0].t == "help":
            await ctx.send("\n".join([*lines, str(cmd) for cmd in self.commands]))
            return
        if ctx.argc != 2:
            await ctx.send(f"Invalid syntax. Expected 2 args, got {ctx.argc}. Check `!v help`")
            return

        self.checkReady()
        self.checkLaunched()

        self.ready = False
        self.v_inner(ctx)
        self.ready = True

    async def v_inner(self, ctx):

        query = ctx[0].t 
        actions = ctx[1].t

        cmds = self.parseCommands(actions)

        fullQuery=f"https://vk.com/{query}"
        self.securityGuard.check(fullQuery)
        await self.scheduler.goto(fullQuery)

        cmdsSession = ChromiumCommandsSession(self.chr, ctx)

        for method,methodargs in cmds:
            try:
                await method(cmdsSession, methodargs) # first args is self, i.e. ChromiumCommandsSession

            except OurException as e:
                e.handleFeedback()
                break

            except Exception as e2:
                await ctx.send(str(e2))
                break

    async def restart(self, ctx):
        self.chr = ChromiumWrapperNew()
        await self.chr.launch()
        self.launched=True
        self.ready = True
        await ctx.send("ок")

async def jseval(self,msg): # user may read files in one folder with empty.html, however, there are no files, temprorarily disabled. Also AJAX with potential malicious payload
    global chr, launched,vReady
    if not vReady: # quite poor sync mechanism
        await u.send(msg, "Command in progress")
        return
    if not launched:
        await chr.launch()
        launched=True
    vReady = False
    await chr.goto(EMPTY_HTML_URL)
    await u.send(msg, await chr.exe(msg.content[2+len("js"):]))
    vReady = True

async def createRoles(self, ctx):
    if ctx.argc != 2:
        await ctx.send("Invalid syntax")
        return
    pattern = ctx[0].t
    types= eval(ctx[1].t)
    for role in (set(types) - {r.name for r in msg.channel.guild.roles if re.match(pattern, r.name)}): # remove dups?
        await u.createRole(ctx.msg, role)

async def showRolesMatchesPattern(self, ctx):
    await ctx.send(" ".join({r.name for r in ctx.guild.roles if re.match(ctx[0].t, r.name)})) # sm?

async def showRolesNotMatchesPattern(self, ctx):
    await ctx.send(" ".join({r.name for r in ctx.guild.roles if not re.match(ctx[0].t, r.name)})) # snm?

class ServerProfilesCommandSystem:
    def __init__(self):
        pass
        
    async def profile(self, ctx):
        a = ctx.args
        if len(a) == 0:
            profileHelp(msg)
            return
        if len(a) == 1:
            pass
