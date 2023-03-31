# F_D_C_Willard

Discord bot originally dedicated to russian MBTI server with ~20 active users out of ~400. Rewriteen version, may not worc, however, you can help with debug
Has integration with chromium (chrome is chromium *extension*) via puppeteer (which is py version of pyppeteer) that allow to grab screenshots, extract data and many other hypothetical things.

## Example of !v output (command to worc with http://vk.com/ pages, may be generalized to any site (nevertheless it may be unsafe to allow anyone to visit any site))

Invalid syntax. Valid is\
!v `urlpart` `actions`\
Page address is 'https://vk.com/' + `urlpart`, should be user or group page or 'search?...'. If the same as in previous command use, don't reload page (for dynamic pages)\
`actions` is semicolon-separated list of build-in functions (use ' ' for str args) (by default funcs are marked __underline__)\
If argument contains spaces, delimit it by " ". If argument should contain ", or \\ place \\ in front of them (\\", \\\\).\
**screenshot**/**s**(selector:str)\
**text**/**t**(selector:str)\
**translatedtext**/**a**(selector:str,target:str='en',source:str='auto')\
**translatedtextwrapped**/**aw**(selector:str,width:int=70,target:str='en',source:str='auto') (Uploads any len as file)\
**html**/**h**(selector:str)\
**remove**/**r**(selector:str)\
**hide**/**d**(selector:str)\
**click**/**c**(selector:str) (currently restricted (primary key, down+up, other confs in eval (as well as **press**)))\
**press**/**p**(key:str,selector:str='body') (same)\
**type**/**y**(selector:str,text:str) (same)\
**eval**/**e**(selector:str) (same)\
**skip**/**k**(selector:str) (there are :not, lol)\
**scroll**/**l**(dx:int,dy:int=0,times:int=1,delayMs:int=0)\
**waitforselector**/**w**(selector:str)\
**setviewpoint**/**v**(width:int,height:int,deviceScaleFactor:float=1.0,isMobile:bool=false,hasTouch:bool=false,isLandscape:bool=false) (bodyHeight for out-of-screen content render)\
__removeAllButWorkspace__() (remove('#fastchat-reforged, #page_header_cont, #side_bar, #stl_left, .group_friends, .people_module'))\
__expandPostsText__() (click('.PostTextMore__content'))\
__skipScripts__() (skip('script'))


## Features
- This chapter is empty

## Requirements:
Python 3+, discord.py, puppeteer, matplotlib, requests, [libretranslate_py](https://github.com/IEEERemainder/libretranslate_py)

## Run guide
This chapter is empty

## TODOS
- Find previous todos list and move it here

## Have ideas or need help? 
Create issue or concat me via nosare@yandex.ru or Interlocked#6505
