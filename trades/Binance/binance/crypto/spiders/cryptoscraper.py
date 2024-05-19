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
    allowed_domains = ["binance.com"]
    start_urls = ["https://www.bitmart.com/trade/en-US?layout=pro&theme=dark&symbol=BTC_USDT"]
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'RETRY_TIMES': 3,  
    }

    def start_requests(self):
        ps=["BTC_USDT","ETH_USDT","ADA_USDT","XRP_USDT"]
        #ps=["BTC_USDT"]
        for p in ps:
            yield scrapy.Request("https://www.binance.com/en/trade/"+p,meta={'playwright':True},callback=self.parse)
            print(p)
            #time.sleep(100)

    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response):
        lock_file = '/shared_lock_files/'+str(response.url[33:].replace("_",""))+'.lock'
        # Attempt to acquire the lock
        cnt2=0
        while os.path.exists(lock_file):
            print("Lock file exists. Waiting to acquire the lock...")
            cnt2+=1
            if cnt2>71800:
                os.remove(lock_file)
            time.sleep(0.5)
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
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080},user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0")
            page = await context.new_page()
            print("###################")
            print("###################")
            print("URL: ",response.url)
            print("###################")
            print("###################")

            await page.goto(response.url)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(30000)

            button_id = 'onetrust-accept-btn-handler'
            button_selector = f'button#{button_id}'
            await page.click(button_selector)
            old_result=""
            cnt=1
            while True:
                temp=0
                # item-col price buy
                xpath = '//body//div[@class="list-item-entity trade-list-item trade-list-item-sell"]'
                xpath2 = '//body//div[@class="list-item-entity trade-list-item trade-list-item-buy"]'
                #xpath = '//body//li[@class="list-item"]//span'
                

                elements_amount = await page.query_selector_all(xpath)
                elements_amount2 = await page.query_selector_all(xpath2)
                #print(elements_amount)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    result_lists.append("sell")
                    result_lists+=text_contentt.split("\n")
                    #print(text_contentt.split("\n"))
                result_lists2=[]
                for element in elements_amount2:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    result_lists2.append("buy")
                    result_lists2+=text_contentt.split("\n")
                    #print(text_contentt.split("\n"))
                
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
                result_lists+=result_lists2
                result_list_of_tuples=[tuple(result_lists[i:i+4]) for i in range(0, len(result_lists), 4)]
                print(result_list_of_tuples)

                url=response.url[33:]
                url = url.replace("_","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                await page.wait_for_timeout(500)
                time.sleep(0.5)
            print("scrap again")
            print("scrap again2")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse)