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
    allowed_domains = ["mexc.com"]
    start_urls = ["https://www.mexc.com/exchange/BTC_USDT"]
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'RETRY_TIMES': 3,  
    }
    def start_requests(self):
        ps=["BTC_USDT","ADA_USDT","ETH_USDT","XRP_USDT"]
        #ps=["BTC_USDT"]#,"ADA_USDT","ETH_USDT","XRP_USDT"]
        for p in ps:
            yield scrapy.Request("https://www.mexc.com/exchange/"+p,meta={'playwright':True},cb_kwargs={'p': p})
            print(ps)
            #time.sleep(100)

    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response,p):
        lock_file = '/shared_lock_files/'+str(p.lower().replace("_",""))+'.lock'
        cnt2=0
        while os.path.exists(lock_file):
            print("Lock file exists. Waiting to acquire the lock...")
            if cnt2>71800:
                os.remove(lock_file)
                cnt2=0
            cnt2+=1
            time.sleep(0.5)
        # Attempt to acquire the lock
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
            browser = await pw.firefox.launch(headless=True,)
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080})
            page = await context.new_page()
            print("###################")
            print("###################")
            print(response.url)
            print("###################")
            print("###################")

            await page.goto(response.url)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(30000)
            old_result=""
            cnt=1
            while True:
                xpath = '//body//div[@class="deals_price__uztEy deals_sell__ZBqnq" or @class="deals_price__uztEy deals_buy__TUl7M" or @class="deals_vol__5h24A" or @class="deals_time__RCCW2"]'
                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    #result_lists.append(text_contentt)
                    if class_name == "deals_price__uztEy deals_buy__TUl7M":
                        print("buy")
                        result_lists.append("buy")
                    if class_name == "deals_price__uztEy deals_sell__ZBqnq":
                        print("sell")
                        result_lists.append("sell")
                    if "Amo" not in text_contentt and "Time" not in text_contentt:
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
                url=p.replace("_","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                await page.wait_for_timeout(1000)
                time.sleep(1)
            print("scrap again")
            yield scrapy.Request("https://www.mexc.com/exchange/"+p,meta={'playwright':True},cb_kwargs={'p': p})