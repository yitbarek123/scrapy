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
    allowed_domains = ["kraken.com"]
    start_urls = [""]
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'RETRY_TIMES': 3,  
    }
    def start_requests(self):
        ps=["btc-usdt","ada-usdt","eth-usdt","xrp-usdt"]
        for p in ps:
            yield scrapy.Request("https://pro.kraken.com/app/trade/"+p,meta={'playwright':True},cb_kwargs={'p': p})
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
        lock_file = '/shared_lock_files/'+str(p.replace("-",""))+'.lock'
        # Attempt to acquire the lock
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
            browser = await pw.firefox.launch(headless=True,)
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080})
            page = await context.new_page()
            print("###################")
            print("###################")
            print(response.url)
            print("###################")
            print("###################")
            await page.goto(response.url)
            await page.wait_for_timeout(30000)
            pp= page.locator(f'//div[contains(text(), "Market trades")]')
            await pp.click()
            await page.wait_for_timeout(30000)
            cnt=1
            old_result=""
            while True:
                xpath = '//div[@class="relative flex min-w-min group px-3"]//span'
                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                result_lists=[]
                t=''
                prev=""
                pp=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    #result_lists.append(text_contentt)
                    #print(text_contentt)
                    
                    #if "text-ds-positive text-ds-kraken-12-medium capitalize ms-ds-0 me-ds-0 mt-ds-0 mb-ds-0" == class_name:
                    #    if "buy" not in pp:
                    #        print("buy")
                    #        result_lists.append("buy")
                    #        prev="buy"
                    #        pp.append("buy")
                            
                    #if "text-ds-negative text-ds-kraken-12-medium capitalize ms-ds-0 me-ds-0 mt-ds-0 mb-ds-0" == class_name:
                    #    if "sell" not in pp:
                    #        print("sell")
                    #        result_lists.append("sell")
                    #        prev="sell"
                    #        pp.append("sell")
                    

                    if "PRICE" not in text_contentt and "TIME" not in text_contentt and "QUA" not in text_contentt:
                        if "AM" in text_contentt or "PM" in text_contentt:
                            result_lists.append(text_contentt.replace(" PM","").replace(" AM",""))
                            print(text_contentt)
                            pp.append(text_contentt)
                        else:
                            if t!=text_contentt:
                                if text_contentt!="":
                                    result_lists.append(text_contentt)
                                    print("yess")
                                    print(text_contentt)
                                    t=text_contentt
                                    pp.append(text_contentt)
                    #TODO get actual tradetype
                    if len(pp)==3:
                        result_lists.append("buy")
                        pp=[]
                
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
                    #os.remove(lock_file)
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
                
                #print(result_lists)
                result_list_of_tuples=[tuple(result_lists[i:i+4]) for i in range(0, len(result_lists), 4)]
                print(result_list_of_tuples)
                url=p.replace("-","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                await page.wait_for_timeout(1000)
                time.sleep(0.5)
        print("print scrapy")
        yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse,cb_kwargs={'p': p})