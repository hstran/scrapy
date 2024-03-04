#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Tao Ran

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
import random
import re
import pandas as pd
from lxml import etree
from lxml.html.clean import Cleaner
import logging
import threading
from tqdm import tqdm

# 禁用警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(level=logging.DEBUG)


def save_data(result):
    write = pd.ExcelWriter("E:\\scrapy\\VOA.xlsx")
    df = pd.DataFrame(result)
    df.to_excel(write, sheet_name='Sheet1', index=False)
    write.close()



def format_string(string: str):
    ret = re.sub(" {2,}", " ", re.sub("([\n\t\r])", " ", string)).strip() if string else ''
    return re.sub(' {2,}', " ", ret)


def clean_style(announcement_body):
    cleaner = Cleaner(style=True)
    text0 = cleaner.clean_html(announcement_body)
    text0 = re.sub(r'(<[^>\s]+\s.*?)class=".*?"\s?(.*?>)', r'\1\2', text0)
    text0 = re.sub(r'(<[^>\s]+\s.*?)id=".*?"\s?(.*?>)', r'\1\2', text0)
    text0 = re.sub(r'(<[^>\s]+\s.*?)align=".*?"\s?(.*?>)', r'\1\2', text0)
    text0 = re.sub(r'<br\s*?/?>', '&nbsp;&nbsp;&nbsp;&nbsp;', text0)
    return text0


def html_to_text(html_string):
    cleaner = Cleaner(style=True)
    text0 = cleaner.clean_html(html_string)
    html = etree.HTML(text0)
    return format_string(html.xpath('string(.)'))


def get_list_data(list_url, list_params):
    time.sleep(random.uniform(1, 3))
    response = requests.get(url=list_url, headers=list_params, verify=False)

    if response.status_code == 200:
        print("Successfully fetched list data!")
    else:
        print(f"Failed to fetch list data, HTTP status code: {response.status_code}")
        return

    html = etree.HTML(response.text)
    list_data = html.xpath("//div[@class='media-block ']")
    for data in list_data:
        title = data.xpath("./div/a/@title")[0]
        link = "https://www.voanews.com" + data.xpath("./div/a/@href")[0]
        get_detail_data(title, link)


def get_detail_data(article_title, article_link):
    time.sleep(random.uniform(1, 3))
    detail_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url=article_link, headers=detail_headers, verify=False)

    if response.status_code == 200:
        print("Successfully fetched detail page data!")
    else:
        print(f"Failed to fetch detail page data, HTTP status code: {response.status_code}")
        return

    html = etree.HTML(response.text)
    article_sources = html.xpath("//a[@class='links__item-link']/text()")
    article_source = article_sources[0].strip() if article_sources else "Unknown"

    article_time = html.xpath("//time[@pubdate='pubdate']/text()")[0]
    body = etree.tostring(html.xpath("//div[@class='wsw']")[0]).decode()
    article_content = html_to_text(body)

    data_unit = {
        "Article Title": article_title,
        "Publication Time": article_time,
        "Article Content": article_content,
        "Article Source": article_source,
        "Article Link": article_link,
    }

    # Use the lock to ensure thread-safety
    lock.acquire()
    try:
        result.append(data_unit)
        print(f"Article Title: {article_title} added to the results.")
    finally:
        lock.release()


def fetch_page_data(page):
    semaphore.acquire()
    try:
        url = base_url.format(page)
        get_list_data(url, headers)
    finally:
        semaphore.release()


if __name__ == "__main__":
    base_url = "https://www.voanews.com/s?k=science%20and%20technology&tab=all&pi={}&r=any&pp=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    result = []

    # 用十个线程池
    semaphore = threading.Semaphore(10)
    lock = threading.Lock()
    threads = []
    # 爬取20页信息
    for page in tqdm(range(1, 20), desc="Processing pages"):
        thread = threading.Thread(target=fetch_page_data, args=(page,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    save_data(result)
