import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from crypto.items import CryptoItem
import os

class CryptoscraperSpider(scrapy.Spider):
    name = "cryptoscraper"
    allowed_domains = ["bitmart.com"]
    start_urls = ["https://www.bitmart.com/trade/en-US?layout=pro&theme=dark&symbol=BTC_USDT"]
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'RETRY_TIMES': 3,  
    }

    def start_requests(self):
        ps=["BTC_USDT","ETH_USDT","ADA_USDT","XRP_USDT"]
        #ps=["BTC_USDT"]
        for p in ps:
            yield scrapy.Request("https://www.bitmart.com/trade/en-US?layout=pro&theme=dark&symbol="+p,meta={'playwright':True})
            print(ps)
            #time.sleep(100)


    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response):
        lock_file = '/shared_lock_files/'+str(response.url[65:].replace("_",""))+'.lock'
        
        cnt2=0
        while os.path.exists(lock_file):
            print("Lock file exists. Waiting to acquire the lock...")
            if cnt2>71800:
                os.remove(lock_file)
                cnt2=0
            cnt2+=1
            time.sleep(0.5)

        while os.path.exists(lock_file):
            print("Lock file exists. Waiting to acquire the lock...")
            time.sleep(1)
        # Create the lock file
        with open(lock_file, 'w') as f:
            f.write('Lock acquired')    
        data = {}
        maxValue=0
        maxToken=""
        #litem=CryptoItem()
        litem=CryptoItem()
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.chromium.launch(headless=True,)
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080})
            page = await context.new_page()
            print("###################")
            print("###################")
            print(response.url)
            print("###################")
            print("###################")

            await page.goto(response.url)

            await page.wait_for_timeout(30000)
            old_result=""
            cnt=1
            while True:
                temp=0
                # item-col price buy
                xpath = '//body//li[@class="list-item"]//span[@class="item-col price buy" or @class="item-col price sell" or @class="item-col count" or  @class="item-col time"]'
                #xpath = '//body//li[@class="list-item"]//span'

                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    direction_name = await page.evaluate('(element) => element.getAttribute("direction")', element)
                    #result_lists.append(text_contentt)
                    t=0
                    t2=0
                    t3=0
                    if class_name == "item-col price buy":
                        #print("buy")
                        result_lists.append("buy")
                        result_lists.append(text_contentt)
                        t=1
                        temp=1
                    if class_name == "item-col price sell" and t==0:
                        #print("sell")
                        result_lists.append("sell")
                        result_lists.append(text_contentt)
                        t=1
                        temp=1
                    if class_name == "item-col time":
                        #print(text_contentt)
                        result_lists.append(text_contentt)
                        t2=2
                    if class_name == "item-col count" and temp==1:
                        print(text_contentt)
                        result_lists.append(text_contentt)
                        t2=3
                    if t==1 and t2==2 and t3==3 and temp==1:
                        print(text_contentt)
                        result_lists.append(text_contentt)
                print(result_lists)
                if old_result=="":
                    if len(result_lists)>0:
                        old_result=result_lists[0]
                if cnt%1200==0:
                    if old_result==result_lists[0]:
                        os.remove(lock_file)
                        print("lock released")
                        cnt=1
                        break
                    old_result=result_lists[0]
                if cnt>72000:
                    #if result_lists[0]==old_result:
                    try:
                        os.remove(lock_file)
                    except:
                        pass
                    print("lock released")
                    cnt=1
                    break
                if cnt>1500:
                    if result_lists==[]:
                        os.remove(lock_file)
                        print("lock released")
                        cnt=1
                        break
                cnt+=1
                print(cnt)
                result_list_of_tuples=[tuple(result_lists[i:i+4]) for i in range(0, len(result_lists), 4)]
                print(result_list_of_tuples)

                url=response.url[65:]
                url = url.replace("_","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                await page.wait_for_timeout(500)
                time.sleep(0.5)

            print("scrap again")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse)