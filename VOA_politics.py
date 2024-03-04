#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Tao Ran

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from lxml import etree
from lxml.html.clean import Cleaner
import re
import pandas as pd

def format_string(string: str):
    ret = re.sub(" {2,}", " ", re.sub("([\n\t\r])", " ", string)).strip() if string else ''
    return re.sub(' {2,}', " ", ret)

def clean_style(announcement_body):
    """
    清洗body格式

    :param announcement_body:
    :return:
    """
    cleaner = Cleaner(style=True)
    text0 = cleaner.clean_html(announcement_body)
    text0 = re.sub(r'(<[^>\s]+\s.*?)class=".*?"\s?(.*?>)', r'\1\2', text0)
    text0 = re.sub(r'(<[^>\s]+\s.*?)id=".*?"\s?(.*?>)', r'\1\2', text0)
    text0 = re.sub(r'(<[^>\s]+\s.*?)align=".*?"\s?(.*?>)', r'\1\2', text0)
    text0 = re.sub(r'<br\s*?/?>', '&nbsp;&nbsp;&nbsp;&nbsp;', text0)  # 将br转换为换行
    return text0

def html_to_text(html_string):
    """
    获取页面纯文本
    :param html_string:
    :return:
    """
    cleaner = Cleaner(style=True)
    text0 = cleaner.clean_html(html_string)
    html = etree.HTML(text0)
    return format_string(html.xpath('string(.)'))

# 代理设置
# 代理设置
proxies = {
    "http": "http://administrator:123qwe,.@222.177.213.242:3310",  # 请替换proxy_ip和proxy_port为正确的值

}

# 获取列表页数据
def get_list_data(list_url, list_params):
    print("开始获取列表数据...")
    list_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    response = requests.get(url=list_url, headers=list_headers, proxies=proxies, verify=False)  # 使用代理
    if response.status_code == 200:
        print("成功获取列表页数据!")
    else:
        print(f"获取列表页数据失败，HTTP状态码：{response.status_code}")
        return

    html = etree.HTML(response.text)
    list_data = html.xpath("//div[@class='media-block-wrap']")
    print(f"找到 {len(list_data)} 条列表数据。")
    for data in list_data:
        titles = data.xpath(".//h4[@class='media-block__title media-block__title--size-3']/text()")
        if titles:
            title = titles[0]
        else:
            print("没有找到标题")
        links = data.xpath(
            "./div[@class='media-block ']/a/@href")
        if links:
            link = links[0]
        else:
            print("没有找到链接")
            continue  # 跳过这条数据，继续下一条

# 获取详情页数据
def get_detail_data(article_title, article_link, article_time):
    print(f"开始获取详情数据，链接：{article_link}")
    detail_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url=article_link, headers=detail_headers, proxies=proxies, verify=False)  # 使用代理

    if response.status_code == 200:
        print("成功获取详情页数据!")
    else:
        print(f"获取详情页数据失败，HTTP状态码：{response.status_code}")
        return

    html = etree.HTML(response.text)
    article_source = html.xpath("//a[@class='links__item-link']/text()")[0].strip()  # 来源
    article_time = html.xpath("//time[@pubdate='pubdate']/text()")[0]  # 具体时间
    body = etree.tostring(html.xpath("//div[@class='wsw']")[0]).decode()
    article_content = html_to_text(body)  # 获取页面纯文本
    data_unit = {
        "文章标题": article_title,
        "发布时间": article_time,
        "文章内容": article_content,
        "文章来源": article_source,
        "文章链接": article_link,
    }
    result.append(data_unit)
    print(f"文章标题：{article_title} 已添加到结果中。")


# 保存数据
def save_data(result):
    write = pd.ExcelWriter("E:\\scrapy\\VOA政治.xlsx")  # 新建xlsx文件。
    df = pd.DataFrame(result)
    df.to_excel(write, sheet_name='Sheet1', index=False)
    write._save()

if __name__ == "__main__":
    url = "https://www.voanews.com/s?k=political%20instability&tab=all&pi=1&r=any&pp=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    result = []
    get_list_data(url, headers)
    save_data(result)  # 保存数据