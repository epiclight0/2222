from seleniumwire import webdriver
import csv 
import re
import pandas as pd
import numpy as np
import time
import json
from urllib import parse
from fake_useragent import UserAgent
from rq import get_current_job


options = {'connection_timeout': None,'suppress_connection_errors': False}



def listToString(res):  
    # initialize an empty string
    str1 = ""  
    # traverse in the string   
    for ele in res:  
        str1 += ele   
    # return string   
    return str1




class urlf:
    def get_url(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--ignore-ssl-errors')
        ua = UserAgent()
        userAgent = ua.random
        chrome_options.add_argument(f'user-agent={userAgent}')
        PATH = "F:\jsprog\start\chromedriver.exe"
        driver = webdriver.Chrome(PATH,options=chrome_options,seleniumwire_options=options)
        query = 0
        lists2 = []
        driver.get(self)
        time.sleep(7)
	    # Access requests via the `requests` attribute
        first_request = driver.requests
        for request in driver.requests:
            if request.response:
                lists2.append(request.url)
        subs = 'https://www.google-analytics.com/j/collect' #keyword
        res = [i for i in lists2 if subs in i]
        for i in res:
            listToString(i)
            url2 = i
            parse.urlsplit(url2)
            parse.parse_qs(parse.urlsplit(url2).query)
            query = dict(parse.parse_qsl(parse.urlsplit(url2).query))
            print(query)
        urlresp = listToString(res)
        time.sleep(8)
        d1 = json.dumps(query)
        resultat = json.loads(d1)
        if resultat:
            driver.quit()
            return resultat
        else:
            resultat = "NO DATA FROM GOOGLE ANALYTICS"
            driver.quit()
            return resultat
    def deb_get_url(self):
        lists2 = []
        lists = []
        driver.get(self)
        time.sleep(7)
	    # Access requests via the `requests` attribute
        first_request = driver.requests
        for request in driver.requests:
            if request.response:
                lists2.append(request.url)
	    # print(lists2) # check for all requests
        subs = 'https://www.google-analytics.com/j/collect' #keyword
        res = [i for i in lists2 if subs in i]
	    #counts = res.count('google-analytics')
	    #print(counts)
        #print (listToString(res)) #get full url of analytics request
        for i in res:
            listToString(i)
            url2 = i
            parse.urlsplit(url2)
            parse.parse_qs(parse.urlsplit(url2).query)
            query = dict(parse.parse_qsl(parse.urlsplit(url2).query))
            print(query)
        urlresp = listToString(res)


        with open('GFG.csv', 'w') as f:
	        # using csv.writer method from CSV package 
            write = csv.writer(f) 
            write.writerows(lists)


	    # sql = "INSERT INTO data (ga, gtm) VALUES (%s, %s)"
	    #val = [
	     # (url, 'Lowstreet 4'),
	    #]
	    # mycursor.executemany(sql, val)
        # mydb.commit()
	    #print(mycursor.rowcount, "was inserted.")
	    #print(val)    

        time.sleep(8)
        driver.close()
        return urlresp