# coding=utf-8
from bs4 import BeautifulSoup
import re
import logging
import smtplib
from email.mime.text import MIMEText
import requests

url_prefix = "https://www.avito.ru"
blacklist_file = "blacklist.file"
logging.basicConfig(filename="sample.log", level=logging.INFO)

no_digit_regex = re.compile(r'[^0-9]*')


def get_page_directly(url):
    return requests.get(url).text


def is_id_in_black_list(id):
    id = no_digit_regex.sub("", str(id))
    try:
        f = open(blacklist_file, 'r')
        for l in f.readlines():
            l_cutted = no_digit_regex.sub("", l)
            if l_cutted == id:
                return True
        f.close()
        f = open(blacklist_file, 'a')
    except IOError:
        f = open(blacklist_file, 'w')
    f.write(str(id) + "\n")
    f.close()
    return False


def get_id_from_url(url):
    id_regex = re.compile(r'_[0-9]*')
    url = url.split("?")[0]  # cut all get params
    tail = id_regex.findall(url).pop()
    return int(tail[1:])


def look_for_suitable_advs():
    logging.debug("start initialization")
    url = "https://www.avito.ru/moskva?q=microsoft+sculpt+ergonomic&i=1"
    source_page = get_page_directly(url)
    logging.debug("got web page")
    s = BeautifulSoup(source_page, "lxml")
    good_blocks = s.findAll('div', 'item_table')
    goods = []
    for block in good_blocks:
        g = good()
        g.title = block.find("a", "item-description-title-link").text.lower()
        g.link = block.find("a", "item-description-title-link").attrs["href"]
        g.date = block.find("div", "date c-2").text.encode('utf-8', errors='replace')
        g.price = int(no_digit_regex.sub("", block.find("div", "about").text))
        goods.append(g)
    logging.debug("blocks with good found. Start filtering")
    looks_good = []
    for g in goods:
        if g.price > 3000:
            continue
        if u"ыш" in g.title and u"лавиатур" not in g.title:
            continue
        if u"ouse" in g.title and u"eyboard" not in g.title:
            continue
        if u'ulpt' not in g.title:
            continue
        if is_id_in_black_list(get_id_from_url(g.link)):
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
if goods:
    print("FOUND SMTH USEFUL!!!\n\n " + "\n\n".join([url_prefix + x.link for x in goods]))