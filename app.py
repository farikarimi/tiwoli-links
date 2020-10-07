import datetime
import json
import urllib.request
import urllib.error
import lxml
import ssl
import re
import math
from bs4 import BeautifulSoup
from timeit import default_timer as timer
from fuzzywuzzy import process, fuzz
from replace_names import replace_names

log = open(f'results/log_{datetime.datetime.today().date()}.txt', 'a')
log.seek(0)
log.truncate()

missing_quote_links = open(f'results/missing_quote_links{datetime.datetime.today().date()}.txt', 'a')
missing_quote_links.seek(0)
missing_quote_links.truncate()

obsolete_links = 0
generated_links = 0
titles_not_found = 0
quotes_found = 0
quotes_not_found = 0
id_link_dict = {}

TAG_LIST = ['p', 'span']

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def print_both(*args):
    text = ' '.join([str(arg) for arg in args])
    print(text)
    log.write(text + '\n')


def read_json(path):
    with open(path, 'r') as json_file:
        quotes = json.load(json_file)
    return quotes


def build_work_link(title, bs):
    global generated_links
    links = []
    title = title.replace(' (Roman)', '')
    if not bs.findAll('a', string=re.compile(title)) and replace_names.get(title):
        title = replace_names.get(title)
        print_both('title was changed to "' + title + '"')
    a_tags = bs.findAll('a', string=re.compile(title))
    if a_tags:
        writer = re.search(r'(?<=/\.\./).*?(?=/)', a_tags[0]['href']).group(0)
        a_tags = [tag for tag in a_tags if writer in tag['href']]
        generated_links += 1
        print_both('tag(s) in html document:', a_tags)
        for tag in a_tags:
            link = re.search(r'(?<=\.\./\.\.).*(?=/.*\.html)', tag['href']).group(0)
            link = 'https://www.projekt-gutenberg.org' + link
            links.append(link)
            print_both('built new link: ' + link)
        return links
    else:
        print_both('title not found')


def find_right_page(url_list, item):
    global quotes_found
    global quotes_not_found
    found_quote = False
    q = re.sub(r'<.*?>', '', item['corpus'])
    quote_substr = q[0:50]
    print_both('first 50 characters of quote: ' + quote_substr + '\n')
    for book_url in url_list:
        if not found_quote:
            try:
                response = urllib.request.urlopen(book_url, context=ctx)
                bsoup = BeautifulSoup(response, 'lxml')
                for li in bsoup.body.ul.findAll('li'):
                    chapter_url = book_url + '/' + li.a['href']
                    if 'titlepage' not in chapter_url:
                        print_both(chapter_url)
                        resp1 = urllib.request.urlopen(chapter_url, context=ctx)
                        soup1 = BeautifulSoup(resp1, 'lxml')
                        text = [t for t in soup1.find_all(text=True) if t.parent.name in TAG_LIST]
                        text = ''.join(text)
                        text = text.replace(u'\u00A0', ' ')
                        # print_both(text)
                        print_both('searching chapter...')
                        match_percent = 100 if quote_substr.lower() in text.lower() \
                            else fuzz.partial_ratio(q.lower(), text.lower())
                        if match_percent >= 80:
                            # TODO: find out why actual 100% matches get a 40-50% partial match score:
                            #  https://stackoverflow.com/questions/39729225/getting-incorrect-score-from-fuzzy-wuzzy-partial-ratio
                            found_quote = True
                            quotes_found += 1
                            print_both('found quote! (', match_percent, '% match)', sep='')
                            print_both('\n', quotes_found, 'quote(s) found')
                            return chapter_url
                        else:
                            print_both('wrong chapter..')
            except urllib.error.HTTPError as e:
                print_both(e.code)
    if not found_quote:
        quotes_not_found += 1
        print_both('\n', quotes_not_found, ' quote(s) not found')
        missing_quote_links.write('title from JSON: ' + item['work']['locales'][0]['name'] + '\n')
        missing_quote_links.write('author: ' + item['work']['author']['locales'][0]['name'] + '\n')
        missing_quote_links.write('quote: ' + q + '\n')
        missing_quote_links.write('first 50 characters of quote: ' + quote_substr + '\n')
        missing_quote_links.write('book URLs:' + str(url_list) + '\n')
        missing_quote_links.write('\n*****************************************************************************\n\n')


def replace_links(quotes):
    all_works_url_resp = urllib.request.urlopen('https://www.projekt-gutenberg.org/info/texte/allworka.html', context=ctx)
    all_works_soup = BeautifulSoup(all_works_url_resp, 'lxml')
    global obsolete_links
    global titles_not_found
    global id_link_dict
    for quote in quotes:
        if 'gutenberg' in quote['href']:
            quote_url = quote['href']
            quote_url_resp = urllib.request.urlopen(quote_url, context=ctx)
            quote_resp_url = quote_url_resp.geturl()
            if quote_url_resp == urllib.error.HTTPError or quote_resp_url != quote_url:
                obsolete_links += 1
                work_title = quote['work']['locales'][0]['name']
                print_both('title from json: ' + work_title)
                author = quote['work']['author']['locales'][0]['name']
                print_both('author: ' + author)
                work_link_list = build_work_link(work_title, all_works_soup)
                if work_link_list:
                    right_link = find_right_page(work_link_list, quote)
                    if right_link:
                        quote['href'] = right_link
                        id_link_dict[quote['id']] = right_link
                else:
                    titles_not_found += 1
                print_both()
                print_both(obsolete_links, 'obsolete link(s) found')
                print_both(generated_links, 'work link(s) generated')
                print_both(titles_not_found, 'title(s) not found')
                print_both('\n**************************************************************\n')
    return quotes


def update_json(path, content):
    upload_json = open(path, 'w')
    json.dump(content, upload_json)
    upload_json.close()


def main():
    print('\nrunning app.py...\n')
    start = timer()

    quotes = read_json('data/tiwolij.json')
    print(len(quotes), 'quotes in total\n')
    updated_quotes = replace_links(quotes)
    print_both('\n', len(quotes), 'quotes in database.\n')
    update_json(path='results/replace_test.json', content=updated_quotes)

    end = timer()
    print('\number of accurate links:', len(id_link_dict))
    print_both('\nellapsed time: ', math.ceil((end - start) / 60), 'minutes')
    print_both('number of quotes with obsolete links:', obsolete_links)
    print_both('number of repaired links:', generated_links)
    log.close()
    missing_quote_links.close()


if __name__ == '__main__':
    main()
