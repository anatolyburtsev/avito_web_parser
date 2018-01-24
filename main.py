# coding=utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import re
import logging
import smtplib
from email.mime.text import MIMEText
import requests

url_prefix = "https://www.avito.ru"
logging.basicConfig(filename="sample.log", level=logging.DEBUG)


def init_phantomjs_driver():
    driver = webdriver.PhantomJS()
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap['phantomjs.page.settings.userAgent'] = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 YaBrowser/17.10.0.2052 Yowser/2.5 Safari/537.36')
    driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=["--ignore-ssl-errors=true"])
    driver.implicitly_wait(20)
    return driver


def init_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


def get_page_by_webdriver(driver, url):
    driver = init_chrome_driver()
    driver.get(url)
    return driver.page_source


def get_page_directly(url):
    return requests.get(url).text


def look_for_suitable_advs():
    logging.debug("start initialization")
    url = "https://www.avito.ru/moskva?q=microsoft+sculpt+Ergonomic&i=1"
    source_page = get_page_directly(url)
    logging.debug("got web page")
    s = BeautifulSoup(source_page, "lxml")
    good_blocks = s.findAll('div', 'item_table')
    digit_regex = re.compile(r'[^0-9]*')
    goods = []
    for block in good_blocks:
        g = good()
        g.title = block.find("a", "item-description-title-link").text.lower()
        g.link = block.find("a", "item-description-title-link").attrs["href"]
        g.date = block.find("div", "date c-2").text.encode('utf-8', errors='replace')
        g.price = int(digit_regex.sub("", block.find("div", "about").text.encode('utf-8', errors='ignore')))
        goods.append(g)
    logging.debug("blocks with good found. Start filtering")
    looks_good = []
    for g in goods:
        if g.price > 13000:
            continue
        if u"ыш" in g.title and u"лавиатур" not in g.title:
            continue
        if u'ulpt' not in g.title:
            continue
        looks_good.append(g)
    logging.debug("After filtering only {} rest".format(len(looks_good)))
    return looks_good


def notify_if_not_empty(looks_good):
    if not looks_good:
        return
    send_email("FOUND SMTH USEFUL!!! " + "\n\n".join([url_prefix + x.link for x in looks_good]),
               'anatolyburtsev@yandex.ru')


def send_email(text, address):
    me = "py bot"
    msg = MIMEText(text)
    msg['Subject'] = 'I\'ve found smth userful!'
    msg['From'] = me
    msg['To'] = address
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [address], msg.as_string())
    s.quit()


class good(object):
    price = 0
    title = ""
    date = ""
    link = ""

    def __str__(self):
        return self.title + str(self.price)


goods = look_for_suitable_advs()
print "FOUND SMTH USEFUL!!!\n\n " + "\n\n".join([url_prefix + x.link for x in goods])
