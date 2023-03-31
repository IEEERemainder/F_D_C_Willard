import ChromeController
import base64
import os
import time
from RepeatedTimer import *

class ChromiumWrapper: # uhhh low level stuff. half-alife, use ChromiumWrapperNew instead
    def __init__(self):
        self.datadir=r'C:\\Users\\Paul\\chrometemp'
        self.additional_options = [f'--user-data-dir={self.datadir}','-disable-gpu','-window-size=1366,768']
        self.state = "INIT"

    def goto(self,t):
        return self.cr.asynchronous_command('Page.navigate', url=t)

    def exe(self,c):
        #print(c)
        raw=self.cr.Runtime_evaluate(expression=c, returnByValue=True)
        #print(raw)
        o=raw['result']['result']
        #print(o)
        if 'value' in o:
            return o['value']
        print("ERROR_JS",o)
        return o # in case of error
        #return self.cr.execute_javascript_statement(c)

    def heartbeat(self):
        self.cr.transport.process_available(self.uuid)
        print("hb",end=" ")

    def hide(self,el):
        self.exe( f"{el}.style['display']='none'")

    def processMsg(self, msg):
        #print("chrome",msg)
        pageLoaded = 'result' in msg and 'frameId' in msg['result']
        if pageLoaded:
            self.state = "PAGE_READY"
            self.onPageReady()

    def load(self):
        self.onPageReady = lambda: 0
        self.crG = ChromeController.ChromeContext(headless=True,binary=r"C:/Users/Paul/AppData/Local/Chromium/Application/chrome.exe", additional_options=self.additional_options)
        self.cr=self.crG.__enter__ ()
        self.goto("about:blank")
        #time.sleep(1)
        self.uuid=list(self.cr.transport.soclist.keys())[0]
        self.cr.transport._message_filters[self.uuid]=[self.processMsg]
        self.heartbeatTimer = RepeatedTimer(1/2, self.heartbeat)
        self.heartbeatTimer.start()

    def unload(self):
        self.heartbeatTimer.cancel()
        self.crG.__exit__()
        os.system("taskkill /IM chrome.exe /f") # kill all no administrator priveleged chrome processes, save ur work or switch to another browser (or rename process lol)
    
    def screenshot(self,el,r,dest): # TODO: add hidescrollbars?
        #el='document.querySelector(".post")' #document.querySelector('.reply_box_wrap')
        for ele in r:
            self.hide(ele)
        rect= self.exe(f'x={el}.getBoundingClientRect(); [x.left, x.top, x.width, x.height]')
        padding=0
        cl= {
            'x': rect[0] - padding,
            'y': rect[1] - padding,
            'width': rect[2] + padding * 2,
            'height': rect[3] + padding * 2,
            'scale':1
        }
        png_bytestring = self.cr.Page_captureScreenshot(captureBeyondViewport=True,clip=cl)
        #print(png_bytestring)
        png_bytestring= base64.b64decode(png_bytestring['result']['data'])
        #print(current_url)
        #f=open(path,mode="wb")
        dest.write(png_bytestring)
        #dest.flush()
        #f.close()
