#!/usr/bin/env python
# encoding:utf-8
"""
@author : llh
@software : PyCharm
@times : 2018/5/21 15:42
"""
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
import requests
import re
from collections import defaultdict

def driver_open(key_word):
    url = "http://xueshu.baidu.com/"
#     driver = webdriver.PhantomJS("D:/phantomjs-2.1.1-windows/bin/phantomjs.exe")
    driver = webdriver.Chrome("D:\\Program Files\\selenium_driver\\chromedriver.exe")
    driver.get(url)
    time.sleep(10)
    driver.find_element_by_class_name('s_ipt').send_keys(key_word)
    time.sleep(2)
    driver.find_element_by_class_name('s_btn_wr').click()
    time.sleep(2)
    content = driver.page_source.encode('utf-8')
    driver.close()
    soup = BeautifulSoup(content, 'lxml')
    return soup

def page_url_list(soup, page=0):
    fir_page = "http://xueshu.baidu.com" + soup.find_all("a", class_="n")[0]["href"]
    urls_list = []
    for i in range(page):
        next_page = fir_page.replace("pn=10", "pn={:d}".format(i * 10))
        response = requests.get(next_page)
        soup_new = BeautifulSoup(response.text, "lxml")
        c_fonts = soup_new.find_all("h3", class_="t c_font")
        for c_font in c_fonts:
            url = "http://xueshu.baidu.com" + c_font.find("a").attrs["href"]
            urls_list.append(url)
    return urls_list



def get_item_info(url):
    print(url)
    # brower = webdriver.PhantomJS(executable_path= r"C:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    # brower.get(url)
    # time.sleep(2)
    # more_text = brower.find_element_by_css_selector('p.abstract_more.OP_LOG_BTN')
    # try:
    #     more_text.click()
    # except:
    #     print("Stopping load more")
    # content_details = brower.page_source.encode('utf-8')
    # brower.close()
    # time.sleep(3)
    content_details = requests.get(url)
    soup = BeautifulSoup(content_details.text, "lxml")
    # 提取文章题目
    title = ''.join(list(soup.select('#dtl_l > div > h3 > a')[0].stripped_strings))
    # 提取文章作者
    authors = ''.join(str(author_) for author_ in list(soup.select('div.author_wr')[0].stripped_strings)[1:])
    # 提取摘要
    abstract = list(soup.select('div.abstract_wr p.abstract')[0].stripped_strings)[0].replace("\u3000", ' ')
    # 提取出版社和时间
    fir_publish_text = list(soup.select('p.publish_text'))
    if len(fir_publish_text) == 0:
        publish_text = "NA"
        publish = "NA"
        year = "NA"
    else:
        publish_text = list(soup.select('p.publish_text')[0].stripped_strings)
        publish = publish_text[0]
        publish = re.sub("[\r\n ]+", "", publish)
        publish_text = ''.join(publish_text)
        publish_text = re.sub("[\r\n ]+", "", publish_text)
        # 提取时间
        match_re = re.match(".*?(\d{4}).*", publish_text)
        if match_re:
            year = int(match_re.group(1))
        else:
            year = 0
    # 提取引用量
    ref_wr = list(soup.select('a.sc_cite_cont'))
    if len(ref_wr) == 0:
        ref_wr = 0
    else:
        ref_wr = list(soup.select('a.sc_cite_cont')[0].stripped_strings)[0]
    # 提取关键词
    key_words = ','.join(key_word for key_word in list(soup.select('div.dtl_search_word > div')[0].stripped_strings)[1:-1:2])
#     data = {
#         "title":title,
#         "authors":authors,
#         "abstract":abstract,
#         "year":int(year),
#         "publish":publish,
#         "publish_text":publish_text,
#         "ref_wr":int(ref_wr),
#         "key_words":key_words
#     }
    return title, authors, abstract, publish_text, year, publish, ref_wr, key_words

def get_all_data(urls_list):
    dit = defaultdict(list)
    for url in urls_list:
        title, authors, abstract, publish_text, year, publish, ref_wr, key_words = get_item_info(url)
        dit["title"].append(title)
        dit["authors"].append(authors)
        dit["abstract"].append(abstract)
        dit["publish_text"].append(publish_text)
        dit["year"].append(year)
        dit["publish"].append(publish)
        dit["ref_wr"].append(ref_wr)
        dit["key_words"].append(key_words)
    return dit

def save_csv(dit):
    data = pd.DataFrame(dit)
    columns = ["title", "authors", "abstract", "publish_text", "year", "publish", "ref_wr", "key_words"]
    data.to_csv("abstract_data.csv", index=False, columns=columns)
    print("That's OK!")



if __name__ == "__main__":
    key_word = "牛肉品质"
    soup = driver_open(key_word)
    urls_list = page_url_list(soup, page=20)
    dit = get_all_data(urls_list)
    save_csv(dit)



