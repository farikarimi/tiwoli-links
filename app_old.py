import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import lxml
import ssl
import re
import json
from app import print_both

with open('data/tiwolij.json', 'r') as json_file:
    quotes = json.load(json_file)

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

TAG_LIST = ['p', 'span']

quotes_found = 0
quotes_not_found = 0


def find_right_page(url_list, item):
    global quotes_found
    global quotes_not_found
    link = ''
    found_quote = False
    quote = re.sub(r'<.*?>', '', item['corpus'])
    # print_both('quote: ' + quote)
    quote_substr = quote[0:50]
    print_both('first 50 characters of quote: ' + quote_substr + '\n')
    for url in url_list:
        if not found_quote:
            try:
                resp = urllib.request.urlopen(url, context=ctx)
                soup = BeautifulSoup(resp, 'lxml')
                for li in soup.body.ul.findAll('li'):
                    chapter_url = url + '/' + li.a['href']
                    if 'titlepage' not in chapter_url:
                        print_both(chapter_url)
                        resp1 = urllib.request.urlopen(chapter_url, context=ctx)
                        soup1 = BeautifulSoup(resp1, 'lxml')
                        text = [t for t in soup1.find_all(text=True) if t.parent.name in TAG_LIST]
                        text = ''.join(text)
                        print_both('searching chapter...')
                        if quote_substr in text:
                            found_quote = True
                            quotes_found += 1
                            print_both('found quote!\n')
                            print_both(quotes_found, 'quote(s) found')
                            link = chapter_url
                            return link
                        else:
                            print_both('wrong chapter..')
            except urllib.error.HTTPError as e:
                print_both(e.code)
    if not found_quote:
        quotes_not_found += 1
        print_both(quotes_not_found, ' quote(s) not found')


# urls = ['https://www.projekt-gutenberg.org/cfmeyer/jenatsch', 'https://www.projekt-gutenberg.org/balzac/eugenie/']
# find_right_page(urls, quotes[1])
