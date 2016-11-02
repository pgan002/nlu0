import os
import re

import requests

import lxml.html


URL_TEMPLATE = 'http://en.wikipedia.org/wiki/List_of_airports_by_IATA_code:_'
DATA_DIR = 'data'


data = []


def get_and_parse_htmls():
  global data
  for char in range(ord('A'), ord('Z')):
    url = URL_TEMPLATE + chr(char)
    print url
    response = requests.get(url)
    doc = lxml.html.fromstring(response.content)
    tables = doc.xpath('body/div/div/div/table')
    assert len(tables) == 1
    trs = tables[0].findall('tr')
    for tr in trs:
      tds = tr.findall('td')
      if len(tds) >= 6:
        row = [unicode(td.text_content()) for td in tds[:4]]  # iata, icao, name, location
        data.append(row)
  print len(data)


def write_parsed_data():
  with open(os.path.join(DATA_DIR, 'airports.csv'), 'w') as f:
    for row in data:
      row = '\t'.join(row).encode('utf8')
      f.write(row + '\n')

