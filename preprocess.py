import pandas as pd
from pandas import DataFrame, Series
import numpy as np
import re
from datetime import datetime
import sys

def convert_required_time_car_to_walk(str):
  if str.find('バス') is not -1:
    matched = re.match(r'((\w+) バス(\d+)分 停歩(\d+)分)', str)
    station = matched.group(2)
    car_time_minute = int(matched.group(3))
    walk_time_minute = int(matched.group(4))
    # Required Time
    ## Walk: 80m/m
    ## Car: 400m/m
    total_walk_time_minutes = int((car_time_minute * 400) / 80) + int(walk_time_minute)
    return '{} 徒歩{}分'.format(station, total_walk_time_minutes)
  return str

def convert_price(str):
  converted = None
  split = str.split('億')
  if len(split) > 1:
    converted = (int(split[0]) * 100000000)
    if split[1] is str:
      converted += (int(split[1]) * 10000)
  else:
    converted = int(split[0]) * 10000
  return converted

try:
  property_df = pd.read_csv('data/properties.csv')

  # Remove useless column
  property_df.drop(['Unnamed: 0'], axis=1, inplace=True)

  # Remove '東京都'
  property_df.address = property_df.address.str.replace('東京都', '')

  # Create address1, address2
  from pandas.core.index import Index, MultiIndex

  def split_address(address):
    split = None
    if address.find('区') is not -1:
      split = address.split('区')
      split[0] = split[0] + '区'
    else:
      split = address.split('市')
      split[0] = split[0] + '市'
    return split

  address_details = property_df.address.apply(split_address).apply(Series)
  address_details.columns = ['address1', 'address2']
  property_df = pd.concat([property_df, address_details], axis=1)
  property_df.drop(['address'], axis=1, inplace=True)

  # Remove rows which '価格' is 価格未定
  property_df = property_df[property_df.price_min != '価格未定']

  # Optimize built_date
  property_df.built_date = property_df.built_date.str.replace('年', '/')
  property_df.built_date = property_df.built_date.str.replace('月', '')
  property_df.built_date = property_df.built_date.str.replace('[予定|下旬]', '')
  property_df.built_date = property_df.built_date.str.replace('即入居可', datetime.now().strftime('%Y/%m'))
  property_df.built_date = property_df.built_date.str.replace('相談', datetime.now().strftime('%Y/%m'))

  # Optimize location
  df_location_line_and_station = property_df.location.str.split('/', expand=True)
  df_location_line_and_station.columns = ['line', 'station']
  df_location_line_and_station.station = df_location_line_and_station.station.apply(convert_required_time_car_to_walk)
  df_location_station_walk_minutes = df_location_line_and_station.station.str.split(' ', expand=True)
  df_location_station_walk_minutes.columns = ['station', 'walk_minutes']
  df_location_station_walk_minutes.walk_minutes = df_location_station_walk_minutes.walk_minutes.replace(r'徒歩(\d+)分', r'\1', regex=True)
  property_df = pd.concat([property_df, df_location_line_and_station.line, df_location_station_walk_minutes], axis=1)
  property_df.drop(['location'], axis=1, inplace=True)

  # Optimaze price
  property_df.price_min = property_df.price_min.str.replace('万円.*', '')
  property_df.price_max = property_df.price_max.str.replace('万円.*', '')
  property_df.price_min = property_df.price_min.str.replace('円台', '')
  property_df.price_max = property_df.price_max.str.replace('円台', '')
  ## round price
  property_df.price_min = property_df.price_min.str.replace('万\d+円.*', '')
  property_df.price_max = property_df.price_max.str.replace('万\d+円.*', '')

  property_df.price_min = property_df.price_min.apply(convert_price)
  property_df.price_max = property_df.price_max.apply(convert_price)

except:
  import pdb; pdb.set_trace()
# Show head of the data
print(DataFrame.head(property_df))
property_df.to_csv('data/preprocessed_properties.csv', encoding='utf-8')
