from pyppeteer import launch
import math
import os

class ChromiumWrapperNew:
    def __init__(self, pathToExecutable, dataDir):
        self.pathToExecutable = pathToExecutable # r"C:/Users/Paul/AppData/Local/Chromium/Application/chrome.exe"
        self.dataDir = dataDir # r'C:/Users/Paul/chrometemp'

    async def launch(self):
        self.browser = await launch(
            headless = True,
            executablePath = self.pathToExecutable,
            userDataDir = self.dataDir,
            autoClose = False,
            defaultViewport = {
                "width" : 1366, 
                "height" : 768, 
                "deviceScaleFactor" : 1.0
            },
            args = ['-disable-gpu']
        )
        self.page = await self.browser.newPage()

    def terminate(self):
        os.system("taskkill /IM chrome.exe /f") # OS-dependant TODO

    async def goto(self, a):
        await self.page.goto(a, {"waitUntil": "domcontentloaded"})

    async def waitForSelector(self, s, timeout=1e5):
        await self.page.waitForSelector(s, timeout=timeout)

    async def exe(self, c):
        return await self.page.evaluate(c)

    async def hide(self, el):
        await self.exe(f"{el}.style['display']='none'")

    async def screenshot(self, el, r): # desprecated, use logic in Commands.py/ChromeCommandsSession/screenshotFn
        await self.page.setViewport({'width':1366, 'height':math.ceil(await self.exe("document.body.getBoundingClientRect().height")), "deviceScaleFactor":1.0,"isMobile":False,"hasTouch":False,"isLandscape":False})

        for ele in r:
            self.hide(ele)

        rect= await self.exe(f'x={el}.getBoundingClientRect(); [x.left, x.top, x.width, x.height]')
        padding=0
        cl= {
            'x': rect[0] - padding,
            'y': rect[1] - padding,
            'width': rect[2] + padding * 2,
            'height': rect[3] + padding * 2,
            'scale':1
        }
        try:
            await self.page.screenshot({"captureBeyondViewport":True,"fromSurface":True,"clip":cl, "path":r"C:\Users\Paul\test.png"})
        except Exception as ex:
            print(ex)
        #f=open(r"C:\Users\Paul\test.png", mode="rb")
        #dest.write(f.read())
        #f.close()
