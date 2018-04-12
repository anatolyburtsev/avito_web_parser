# coding=utf-8
from bs4 import BeautifulSoup
import re
import logging
import smtplib
from email.mime.text import MIMEText
import requests
from avito_url import AvitoUrl

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


def look_for_suitable_advs(query, min_price, max_price):
    logging.debug("start initialization")
    url = AvitoUrl(query).set_prices(min_price, max_price).get_url()
    source_page = get_page_directly(url)
    logging.debug("got web page")
    s = BeautifulSoup(source_page, "lxml")
    good_blocks = s.findAll('div', 'item_table')
    goods = []
    for block in good_blocks:
        g = Good()
        g.title = block.find("a", "item-description-title-link").text.lower()
        g.link = block.find("a", "item-description-title-link").attrs["href"]
        # g.date = block.find("div", "date c-2").text.encode('utf-8', errors='replace')
        try:
            g.price = int(no_digit_regex.sub("", block.find("div", "about").text))
        except:
            raise Exception(block.text)
        goods.append(g)
    logging.debug("blocks with good found. Start filtering")
    looks_good = []
    for g in goods:
        if u"trackpad" not in g.title or u"2" not in g.title:
            continue
        if u"mouse" in g.title:
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


class Good(object):
    price = 0
    title = ""
    date = ""
    link = ""

    def __str__(self):
        return self.title + str(self.price)


goods = look_for_suitable_advs("apple magic trackpad 2", 2500, 4500)
if goods:
    print("FOUND SMTH USEFUL!!!\n\n " + "\n\n".join([url_prefix + x.link for x in goods]))
