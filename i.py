import requests
from telethon.sync import events,TelegramClient, Button, events 
from bs4 import BeautifulSoup
import asyncio
import requests
from datetime import date
import datetime
import os
import os.path
import time
api_id = 1286167
api_hash = 'a41691f6c0b646c222b9c5559f0ac116'
client = TelegramClient('client', api_id, api_hash)
client.start()
bot = TelegramClient('bot', api_id, api_hash)
bot.start(bot_token="1144044250:AAFk93xAVG7g3_okHFVU6w9UUlTTb6dhTag")
bot.parse_mode="html"
print("Bot iniziato")
async def read(f):
    file=open(f,"r")
    return file.read()
    file.close()
async def append(f,txt):
    file=open(f,"a+")
    file.write(txt)
    file.close()
async def write(f,txt):
    file=open(f,"wb+")
    file.write(txt)
    file.close()
async def writes(f,txt):
    file=open(f,"w+")
    file.write(txt)
    file.close()
async def strtofloat(s):
    pre=s.replace(",","").replace(".","").replace("€","")[:len(s.replace(",","").replace(".","").replace("€",""))-2]
    post=s.replace(",","").replace(".","").replace("€","")[len(s.replace(",","").replace(".","").replace("€",""))-2:]
    return float(pre+"."+post)
async def log(txt):
    f=open("file.txt","w+", encoding='utf-8')
    f.write(txt)
    f.close()
async def upload(url):
    print("Upload immagine")
    h = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})
    c=requests.get(url,headers=h).content
    await write("img.png",c)
    return requests.post("https://prezz1.altervista.org/wp-json/wp/v2/media",headers={"Authorization":"Basic THVjYTpOYXBvbGkxMDFA",'Content-Disposition' : 'attachment; filename="test1.jpg"'},files={"file":open("img.png","rb")}).json()["id"]
async def post(json):
    print("Postando prodotto sul sito")
    if(json["op"]=="0€"):
        exc="A "+json["p"]+""
    else:
        exc="Da "+json["op"]+" a "+json["p"]
    exc=exc+" <h1><a href='"+json["url"]+"'>Vai</a></h1>"
    requests.post("https://prezz1.altervista.org/wp-json/wp/v2/posts",headers={"Authorization":"Basic THVjYTpOYXBvbGkxMDFA"},data={"status":"publish","title":json["title"],"format":"link","excerpt":exc,"content":exc,"featured_media":await upload(json["image"])}).text
async def toc(json):
    h = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})
    msg="""⚠️PREZZONE⚠️
"""+json["title"]+"""

💶PREZZO:"""+json["p"]+"""💶:(invece di:💰"""+json["op"]+"""💰)

SCONTO:📉"""+json["percentage"]+"""📉
Categoria:"""+json["category"]
    bts=[[Button.url("Acquista prodotto", url=json["url"])]]
    await bot.send_file("https://t.me/Prezz1",requests.get(json["image"],headers=h).url,caption=msg,buttons=bts,force_document=False)
async def check_message(json):
    m=int(time.strftime("%M"))
    lm=int(await read("botm"))+5
    dif=lm-m
    if(m>=lm or dif>=5):
        print("Controllando informazione prodotto")
        today = date.today()
        if(json["op"]!="0€"):
            m=int(time.strftime("%M"))
            op=float(json["op"].replace(",",".").replace("€",""))
            p=float(json["p"].replace(",",".").replace("€",""))
            ratio=p/op
            if(ratio<0.7):
                if(json["p"]!=json["op"]):
                    await post(json)
                    await toc(json)
                await writes("botm",str(m))
        await append(str(today),json["url"].split("/dp/")[1].split("?")[0])
async def scrape(asin):
    global html,soup,tc
    today = date.today()
    yesterday= str(datetime.datetime.today() - datetime.timedelta(days=1)).split(" ")[0]
    m=int(time.strftime("%M"))
    lm=int(await read("botm"))+10
    dif=lm-m
    print(m,lm,dif)
    cc=lm-10
    print(m,cc)
    cc=m<cc
    if(m>=lm or cc):
        print("ciao")
        try:
            os.remove(yesterday)
        except:
            oo=""
        i=0
        if os.path.exists(str(today)):
            if asin not in await read(str(today)):
                i=i+1
        else:
            i=i+1
        if i>0:
            print("Ottenendo informazione prodotto")
            product={}
            url="https://amazon.it/dp/"+asin
            h = ({'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                    'Accept-Language': 'en-US, en;q=0.5'})
            html=requests.get(url,headers=h).text
            soup=BeautifulSoup(html,"lxml")
            tc=soup.find("p",{"class":"a-last"})
            while(tc is not None):
                await asyncio.sleep(5)
                html=requests.get(url,headers=h).text
                soup=BeautifulSoup(html,"lxml")
                tc=soup.find("p",{"class":"a-last"})
            i=0
            try:
                product["op"]=soup.find("div",{"id":"apex_desktop"}).find("span",{"data-a-strike":"true"}).findAll("span",{"class":"a-offscreen"})[0].text
                i=i+1
            except:
                print("no op")
            try:
                product["p"]=soup.find("div",{"id":"apex_desktop"}).find("span",{"class":"priceToPay"}).find("span",{"class":"a-offscreen"}).text
                i=i+1
            except:
                print("no p")
            if(product.get("p") is None):
                product["p"]="0€"
            if(product.get("op") is None):
                product["op"]="0€"
            if(await strtofloat(product["p"])>await strtofloat(product["op"])):
                ii=product["op"]
                product["op"]=product["p"]
                product["p"]=ii
            if(product["p"]=="0€"):
                cc=product["p"]
                product["p"]=product["op"]
                product["op"]=cc
            #se il cammello sbaglia leva questo ---
            #try:
                #html=requests.get("https://it.camelcamelcamel.com/product/"+asin,headers=h).text
                #print(html)
                #product["op"]=html.split('<td>Media <sup>+</sup></td>')[1].split('<td>')[1].split('</td>')[0].replace(".","")
            #except:
                #print("no camel op")
            #---
            try:
                product["title"]=soup.find("span",{"id":"productTitle"}).text.strip()
            except:
                print("no title")
            try:
                if(i>1):
                    p=await strtofloat(product["p"])
                    op=await strtofloat(product["op"])
                    percentage=p/op
                    percentage=percentage*100
                    percentage=100-percentage
                    product["percentage"]="-"+str(round(percentage))+"%"
            except:
                print("no percentage")
            try:
                index=soup.find("select",{"class":"nav-search-dropdown"})["data-nav-selected"]
                product["category"]=soup.find("select",{"class":"nav-search-dropdown"}).findAll("option")[int(index)].text
            except:
                print("no category")
                await log(html)
            try:
                product["url"]=url+"?tag=luke300011-21"
            except:
                print("no url")
            try:
                product["image"]="https://ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=IT&ASIN="+asin+"&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_AC_SX425_"
            except:
                try:
                    product["image"]=soup.findAll("div",{"id":"imgTagWrapperId"})[0].find("img")["src"]
                except:
                    product["image"]="https://prezz1.altervista.org/wp-content/uploads/2021/12/cropped-IMG_20211211_203428_184.jpg"
            await check_message(product)
@client.on(events.NewMessage(chats=("https://t.me/amzn_discount","@prezzipazzeschi","@misterprezzo","https://t.me/scontierisparmio","https://t.me/testoneeeee","https://t.me/amazon_angrese","https://t.me/testoneeeee","https://t.me/canalifighi","https://t.me/techbestdeals","https://t.me/le_offerte_dal_web_group","https://t.me/affarometro","https://t.me/overVoltOfficial","https://t.me/stockdroid2","https://t.me/stockdroid","https://t.me/glierroristidelweb","https://t.me/stockdroid")))
async def handler(event):
    now = datetime.datetime.now()
    if(now.hour<22 and now.hour>=10):
        # Respond whenever someone says "Hello" and something else
        print("Trovato nuovo messaggio")
        print(event)
        l=[]
        e=str(event).rstrip()
        e=e.split('http://www.amazon.it')
        e.pop(0)
        for el in e:
            el=el.split(' ')[0].split("'")[0].split('"')[0]
            el=el.split('B0')
            el.pop(0)
            for v in el:
                asin="B0"+v[:8]
                if(asin.isalnum()):
                    if asin not in l:
                        l.append(asin)
                        await scrape(asin)
        e=str(event).rstrip()
        e=e.split("https://www.amazon.it")
        e.pop(0)
        for el in e:
            el=el.split(' ')[0].split("'")[0].split('"')[0]
            el=el.split('B0')
            el.pop(0)
            for v in el:
                asin="B0"+v[:8]
                if(asin.isalnum()):
                    if asin not in l:
                        l.append(asin)
                        await scrape(asin)
        e=str(event).rstrip()
        e=e.split("https://amazon.it")
        e.pop(0)
        for el in e:
            el=el.split(' ')[0].split("'")[0].split('"')[0]
            el=el.split('B0')
            el.pop(0)
            for v in el:
                asin="B0"+v[:8]
                if(asin.isalnum()):
                    if asin not in l:
                        l.append(asin)
                        await scrape(asin)
        e=str(event).rstrip()
        e=e.split("http://amazon.it")
        e.pop(0)
        for el in e:
            el=el.split(' ')[0].split("'")[0].split('"')[0]
            el=el.split('B0')
            el.pop(0)
            for v in el:
                asin="B0"+v[:8]
                if(asin.isalnum()):
                    if asin not in l:
                        l.append(asin)
                        await scrape(asin)
        e=str(event).rstrip()
        e=e.split("https://amzn.to/")
        e.pop(0)
        for v in e:
            url=requests.get("https://amzn.to/"+v[:7]).url
            url=url.split('B0')
            url.pop(0)
            for v in url:
                asin="B0"+v[:8]
                if(asin.isalnum()):
                    if asin not in l:
                        l.append(asin)
                        await scrape(asin)
client.run_until_disconnected() 
