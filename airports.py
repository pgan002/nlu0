import itertools
import os
import re
import string

import requests

import lxml.html


URL_TEMPLATE = 'http://en.wikipedia.org/wiki/List_of_airports_by_IATA_code:_'
AIRPORTS_DATA_FILE = 'data/airports.csv'
AIRPORTS_HTML_DIR = 'data/airports'


airports_list = []  # Each element is a list of IATA code, ICAO code, name, location
airports_dict = {}


def _get_html_file_path(char):
  return os.path.join(AIRPORTS_HTML_DIR, char + '.html')


def maybe_download_htmls():
  if not os.path.isdir(AIRPORTS_HTML_DIR):
    os.mkdir(AIRPORTS_HTML_DIR)

  for char in string.uppercase:
    if not os.path.isfile(_get_html_file_path(char)):
      url = URL_TEMPLATE + char
      print url
      response = requests.get(url)
      with open(_get_html_file_path(char), 'w') as f:
        f.write(response.content)


def parse_htmls():
  global airports_list
  for char in string.uppercase:
    doc = lxml.html.parse(_get_html_file_path(char))
    tables = doc.xpath('body/div/div/div/table')
    assert len(tables) == 1
    trs = tables[0].findall('tr')
    print char,

    ref_re = re.compile(r'(.+?)\[[0-9]+\](.*?)')
    row_count = 0
    for tr in trs:
      tds = tr.findall('td')
      match = None
      if len(tds) >= 4:
        row = []
        for td in tds[:4]:
          text = td.text_content().replace('\n', ' ').replace('\t', ' ')
          # Strip any reference links like text[1]
          match = ref_re.match(text)
          if match:
            text = match.group(1) + match.group(2)
          row.append(unicode(text))
        airports_list.append(row)
        row_count += 1
    print row_count

  print len(airports_list)


def write_list():
  '''Write the list as a tab-separated file'''
  with open(AIRPORTS_DATA_FILE, 'w') as f:
    for row in airports_list:
      row = '\t'.join(row).encode('utf8')
      f.write(row + '\n')


def read_list():
  '''Read tab-separated file of airport data'''
  global airports_list
  
  airports_list = [line.strip().split('\t')
                   for line in open(AIRPORTS_DATA_FILE)]


importance_pat = r"(?P<importance>Domestic|Regional|International|Int'l|Memorial)"
category_pat = r'(?P<category>Airport|Airfield|Airstrip|Aircraft Field|Field|Airpark|Aerodrome|Air Base|Air Force Base|Seaplane Base|RAF|Airbase|Air Park|Waterport|Jetport|Air Center|Air and Space Port|Sunport)'
name_pat = r'(?P<name>.+?)( {})? {}'.format(importance_pat, category_pat)
paren_pat = r'(?P<prefix>.+) \((?P<parenthesized>.+)\)(?P<suffix>.*)'


def compile_dict():
  '''Compile airport codes, names and locations for efficient matching'''
  global airports_dict
    
  # Pattern for splitting off parenthesized expressions in names and locations
  paren_re = re.compile(paren_pat)

  for i, (iata, icao, full_name, location) in enumerate(airports_list):
    airports_dict[iata] = iata
    airports_dict[icao] = iata
    
    # Enter parenthesized parts of an airport name sepaately as an alternative name
    paren_match = paren_re.match(full_name)
    if paren_match:
      airports_dict[paren_match.group('parenthesized')] = iata
      full_name = paren_match.group('prefix') + paren_match.group('suffix')
      airports_list[i][2] = full_name
    airports_dict[full_name] = iata

    # Enter location names in various combinations
    # Alternative location may be parenthesized
    paren_match = paren_re.match(location)
    if paren_match:
      location = paren_match.group('prefix') + paren_match.group('suffix')
    location_parts = location.split(', ')
    if paren_match:
      location += paren_match.group('parenthesized')
    for l in range(len(location_parts)):
      for subset in itertools.combinations(location_parts, l):
        name = ' '.join(subset)
        airports_dict[name] = iata
    
  # Enter short names in a separate loop to avoid name conflicts
  airport_name_re = re.compile(name_pat)
  for iata, icao, full_name, location in airports_list:
    name_match = airport_name_re.match(full_name)
    if not name_match:
      continue  # There is no shorter name
    short_name = name_match.group('name')
    category = name_match.group('category') or ''
    categorized_name = short_name + ' ' + category
    international_name = short_name + ' International Airport'
    intl_name = short_name + " Int'l Airport"

    # If there are two airports with the same name, the short name should refer
    # to the more major airport
    if full_name != categorized_name \
        and international_name not in airports_dict \
        and intl_name not in airports_dict:
      airports_dict[short_name] = iata
      airports_dict[categorized_name] = iata
    else:
      print short_name


parse_htmls()
write_list()
compile_dict()
