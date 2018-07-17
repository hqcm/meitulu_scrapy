#采用requests+xpath的方法来获取内容
import logging

import requests
from lxml import etree

logger=logging.getLogger(__name__)

def get_html(url):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    html=requests.get (url,headers=headers).content
    return etree.HTML(html)

def fetch_kuaidaili_proxies():
    #这里网站好像不咋地
    for number in range (1,3):
        url='https://www.kuaidaili.com/free/inha/'+str(number)
        html=get_html(url)
        proxy_list=[]
        ips=html.xpath('//td[@data-title="IP"]/text()')
        ports=html.xpath('//td[@data-title="PORT"]/text()')
        #获取的http为大写，需要变换成小写，否则requests无法识别
        types=[item.lower() for item in html.xpath('//td[@data-title="类型"]/text()')]
        speeds=html.xpath('//td[@data-title="响应速度"]/text()')
        for i in range(len(ips)):
            ip=types[i]+'://'+ips[i]+':'+ports[i]
            proxy={types[i]:ip}
            # 输出延迟小于2秒的代理
            if float(speeds[i][:-1]) < 2 and check_proxies(proxy) :
                proxy_list.append(ip)
    return proxy_list

def fetch_xicidaili_proxies():
    url='http://www.xicidaili.com/nn/'
    html=get_html(url)
    proxy_list=[]
    #[2]表示第二个td标签（标签序号不是从0开始，而是从1开始）
    ips=html.xpath('//tr/td[2]/text()')
    ports=html.xpath('//tr/td[3]/text()')
    #获取的http为大写，需要变换成小写，否则requests无法识别
    types=[item.lower() for item in html.xpath('//tr/td[6]/text()')]
    #获取每个代理存活的时间
    survive_times=html.xpath('//tr/td[9]/text()')
    for i in range(len(ips)):
        ip=types[i]+'://'+ips[i]+':'+ports[i]
        proxy={types[i]:ip}
        #直接剔除存活时间只有分钟级的代理
        if '分钟' not in survive_times[i] and check_proxies(proxy):
            proxy_list.append(ip)
    return proxy_list

def check_proxies(proxy):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    crawl_url='https://www.meitulu.com/'
    try:
        #proxies的格式是一个字典,例如{‘http’: ‘http://42.84.226.65:8888‘}
        #使用免费代理爬取目标网页, 如果能够爬下来并且比较过内容之后发现确实是目标网页, 则认为这个代理可用.
        r=requests.get(crawl_url, headers=headers,proxies=proxy, timeout=5)
        if r.status_code == 200 and r.url==crawl_url:
            return proxy
        else:
            return False
    except:
        logger.warning ('invalid %s' % proxy) 
    s = requests.session()
    s.keep_alive = False
            
def fetch_free_proxies():
    #return fetch_kuaidaili_proxies()+fetch_xicidaili_proxies()
    return fetch_xicidaili_proxies()

if __name__=='__main__':
    ip_list=fetch_free_proxies()
    with open('ip_list.txt', 'a') as f:
        for ip in ip_list:
            f.write(ip+'\n')
