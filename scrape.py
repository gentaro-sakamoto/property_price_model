from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import Series, DataFrame
import time
import re
import sys

def trim(str):
  trimmed = re.sub('[(（].*[）)]', '', str)
  trimmed = re.sub('[\t\n\r]', '', trimmed)
  trimmed = re.sub('入居時期：', '', trimmed)
  trimmed = re.sub('[上中下]旬予定', '', trimmed)
  trimmed = re.sub('／予定', '', trimmed)
  trimmed = re.sub('m2', '', trimmed)
  trimmed = re.sub('※1000万円単位', '', trimmed)
  trimmed = re.sub('※権利金含む.*', '', trimmed)
  return trimmed

def extract_min_max(str):
  min_to_max = None
  if str.find('、') != -1:
    min_to_max = str.split('、')[0]
  if str.find('、') != -1:
    min_to_max = str.split('、')[0]
  if str.find('・') != -1:
    min_to_max = str.split('・')[0]

  if min_to_max is not None:
    if min_to_max.find('～') != -1:
      return min_to_max.split('～')
    else:
      return min_to_max
  if str.find('～') is not -1:
    return str.split('～')
  return str

def get_soup_by_page(num=1):
  url = "http://suumo.jp/jj/bukken/ichiran/JJ011FC001/?pc=100&bs=010&bknlistmodeflg=1&po=0&pj=1&nf=&mf=&hf=&sbf=&ohf=&ta=13&urlFlg=1&jspIdFlg=4&lbp=1&sc=13101&sc=13102&sc=13103&sc=13104&sc=13105&sc=13113&sc=13106&sc=13107&sc=13108&sc=13118&sc=13121&sc=13122&sc=13123&sc=13109&sc=13110&sc=13111&sc=13112&sc=13114&sc=13115&sc=13120&sc=13116&sc=13117&sc=13119&sc=13201&sc=13202&sc=13203&sc=13206&sc=13207&sc=13208&sc=13209&sc=13210&sc=13211&sc=13212&sc=13213&sc=13214&sc=13215&sc=13219&sc=13224&sc=13225&sc=13229&kb=1&kt=9999999&km=0&mb=0&mt=9999999&ar=030&ekTjCd=&ekTjNm=&tj=0&et=9999999&pn={}".format(num)
  result = requests.get(url)
  c = result.content.decode('utf-8')
  return BeautifulSoup(c)

soup = get_soup_by_page()
max_page = int(soup.select('ol.pagination-parts li a')[-1].text)

names = []
addresses = []
locations = []
build_date = []
prices_min = []
prices_max = []
floor_plans_min = []
floor_plans_max = []
areas_min = []
areas_max = []

for i in range(1, max_page+1):
  soup = get_soup_by_page(i)
  try:
    for j in range(len(soup.select('div.cassette.property_unit'))):
      cassette = soup.select('div.cassette.property_unit')[j]
      names.append(trim(cassette.find('h2').text))
      # print(trim(cassette.find('h2').text))
      addresses.append(trim(cassette.select('div.ui-text_bold')[0].text))
      locations.append(trim(cassette.select('ul.cassette-text li')[1].text))
      build_date.append(trim(cassette.select('ul.cassette-text li')[2].text))

      result = extract_min_max(trim(cassette.select('span.cassette-price-accent')[0].text))
      if type(result) == list:
        price_min, price_max = result
      else:
        price_min = price_max = result

      prices_min.append(price_min)
      prices_max.append(price_max)

      result = extract_min_max(trim(cassette.select('ul.cassette-plan li')[0].text))
      if type(result) == list:
        fp_min, fp_max = result
      else:
        fp_min = fp_max = result

      floor_plans_min.append(fp_min)
      floor_plans_max.append(fp_max)

      result = extract_min_max(trim(cassette.select('ul.cassette-plan li')[1].text))
      if type(result) == list:
        area_min, area_max = result
      else:
        area_min = area_max = result

      areas_min.append(area_min)
      areas_max.append(area_max)

  except:
    print('err: page{} {}'.format(i, trim(cassette.find('h2').text)))
    print("Unexpected error:", sys.exc_info()[0])

print(len(names))
property_df = \
  pd.concat(
    [Series(names),
    Series(addresses),
    Series(locations),
    Series(build_date),
    Series(prices_min),
    Series(prices_max),
    Series(floor_plans_min),
    Series(floor_plans_max),
    Series(areas_min),
    Series(areas_max)],
    axis=1
  )
property_df.columns = ['name', 'address', 'location', 'built_date', 'price_min', 'price_max', 'plan_min', 'plan_max', 'area_min', 'are_max']
property_df.to_csv('data/properties.csv', encoding='utf-8')
