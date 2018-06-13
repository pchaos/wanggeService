# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : proxy.py

Description :

@Author :       pchaos

date：          18-6-13
-------------------------------------------------
Change Activity:
               18-6-13:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

import requests
"""
# your spider code

def getHtml():
    # ....
    retry_count = 5
    proxy = get_proxy()
    while retry_count > 0:
        try:
            html = requests.get('https://www.example.com', proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 出错5次, 删除代理池中代理
    delete_proxy(proxy)
    return None
    
"""
PROXYSERVER = 'http://123.207.35.36'
# PROXYSERVER = 'http://127.0.0.1'

def get_proxy(ip=PROXYSERVER, port=5010):
    return requests.get("{}:{}/get/".format(ip, port)).content

def delete_proxy(proxy, ip=PROXYSERVER, port=5010):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

