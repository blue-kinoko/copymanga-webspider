from bs4 import BeautifulSoup
import re
import os
import urllib.request
import time
import urllib
import ssl
import threading
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from queue import Queue

class producer(threading.Thread):
    def __init__(self,page_url_queue,img_url_queue,*args,**kwargs):
        super(producer,self).__init__(*args,**kwargs)
        self.page_url_queue=page_url_queue
        self.img_url_queue=img_url_queue
    def run(self):
        while True:
            if self.page_url_queue.empty():
                break
            page_url=self.page_url_queue.get()
            self.parse_url(page_url)

    def parse_url(self,url):
        url_test = 'https://www.copymanga.org' + url
        browser_test = webdriver.Firefox(
            executable_path='D:\BaiduNetdiskDownload\geckodriver-v0.31.0-win64\geckodriver.exe', options=options)
        browser_test.get(url_test)
        time.sleep(3)
        browser_test.find_element(by=By.XPATH, value='/html/body/div[2]/div/ul/li[1]/img').click()
        for i in range(0, 1000):
            browser_test.execute_script("window.scrollBy(0,1)")
        soup_test = BeautifulSoup(browser_test.page_source, 'lxml')
        pic_content = soup_test.find_all('div', class_='container-fluid comicContent')
        pic_links = re.findall(r'data-src="(.*?)"', str(pic_content))
        title = re.findall(r'>(.*?)<',str(soup_test.find_all('h4',class_='header')))[0]
        title=re.sub('/',' ',title)
        browser_test.quit()
        n=0
        for pic_link in pic_links:
            self.img_url_queue.put((pic_link,title,n))
            n+=1

class comsumer(threading.Thread):
    def __init__(self,page_url_queue,img_url_queue,*args,**kwargs):
        super(comsumer,self).__init__(*args,**kwargs)
        self.page_url_queue=page_url_queue
        self.img_url_queue=img_url_queue
    def run(self):
        while True:
            if self.page_url_queue.empty() and self.img_url_queue.empty():
                break
            pic_link,title,num=self.img_url_queue.get()
            try:
                if os.path.exists('./?????????????????????/%s' % title) == False:
                    os.makedirs('./?????????????????????/%s' % title)
            except Exception as e:
                print(e)
            print('----------????????????%s???%s???-----------'%(title,num))
            urllib.request.urlretrieve(pic_link, './?????????????????????/%s/%s.jpg' % (title, num))
            print('----------????????????%s???%s???-----------'%(title,num))
if __name__=='__main__':
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(executable_path='D:\BaiduNetdiskDownload\geckodriver-v0.31.0-win64\geckodriver.exe',
                                options=options)
    browser.get('https://www.copymanga.org/comic/yinvyouxishijieduilurenjuesehenbuyouhao')
    href_pattern = re.compile(r'<a href="(.*?)"')
    title_pattern = re.compile((r'title="(.*?)"'))
    ssl._create_default_https_context = ssl._create_unverified_context
    if os.path.exists('./?????????????????????') == False:
        os.makedirs('./?????????????????????')
    time.sleep(3)
    open_1 = browser.find_element(By.XPATH, value='/html/body/main/div[2]/div[3]/div[1]/div[2]/div/div[1]/ul[1]')
    open_1.click()
    soup = BeautifulSoup(browser.page_source, 'lxml')
    links = soup.find_all('div', class_='tab-pane fade show active')
    hrefs = re.findall(href_pattern, str(links))
    hrefs = list(filter(lambda x: x != 'javascript:;', hrefs))
    titles = re.findall(title_pattern, str(links))
    browser.quit()
    page_url_queue=Queue(len(hrefs))
    img_url_queue=Queue(1000)
    try:
        for href in hrefs:
            page_url_queue.put(href)
        for x in range(5):
            t = producer(page_url_queue, img_url_queue)
            t.start()
        for x in range(5):
            t = comsumer(page_url_queue, img_url_queue)
            t.start()
    except Exception as e:
        print(e)
        quit()



