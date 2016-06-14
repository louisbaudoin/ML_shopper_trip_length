# Import dependencies
from __future__ import division
import pandas as pd
import csv
import numpy as np
import datetime #from datetime import datetime
import calendar #necessary to convert a timestamp into a date
import time
from math import sqrt
import numpy.random as random
from datetime import datetime
import time
from datetime import datetime
from sklearn import preprocessing

# Compute delta for training set and make X_train and X_test same format
def preprocess_train(data):
  # compute shopping time
  _compute_shopping_time(data)
  # Compute xtrain and ytrain
  y_train = data[['trip_id', 'trip_length']]
  del data['shopping_ended_at']
  del data['trip_length']
  X_train = data
  return {'X_train': data, 'y_train': y_train}


def process_data(data, data_items, raw_data):
  # compute shopping time
  _compute_shopping_time(data)
  # change fulfillment model (1: first model, 0: second model)
  data = _change_model(data)
  # Add hour of day_of_week
  data['hour'] = data['shopping_started_at'].map(lambda date: str(date.hour))
  # add day of week
  data['day_of_week'] = data['shopping_started_at'].map(lambda date: str(date.weekday()))
  # delete shopping started at
  del data['shopping_started_at']
  del data['shopping_ended_at']
  # set trip_id as index
  data.set_index('trip_id', drop = True, inplace = True)
  # add dpt count
  count_dpt = _count_departments(data_items)
  data = data.merge(count_dpt, right_index = True, left_index = True, how = "left")
  # item count
  data = data.merge(_items_count(data_items), right_index = True, left_index = True, how = 'left')
  # shopper categorization
  shopper_categorization = _categorization_shoppers(raw_data)
  data = data.merge(shopper_categorization, left_on = 'shopper_id', right_index = True, how = 'left')
  del data['shopper_id']
  return data

# # Calculate delta
# def _calculate_delta(row):
#   delta = row['shopping_ended_at'] - row['shopping_started_at']
#   return delta.seconds

def _compute_shopping_time(data):
  # shopping started_at and shopping_ended_at to string
  data['shopping_started_at'] = data['shopping_started_at'].map(lambda date: datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
  data['shopping_ended_at'] = data['shopping_ended_at'].map(lambda date: datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
  # compute delta
  data['trip_length'] = data.apply(lambda row: row['shopping_ended_at'] - row['shopping_started_at'], axis = 1)
  data['trip_length'] = data['trip_length'].map(lambda x: x.seconds)
  return data

## Convert shopping_ended_at from string to timestamp
def _convert_to_ts(data, var):
  data[var] = data[var].map(lambda date: datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
  return None

def _change_model(data):
  data['fulfillment_model'] = data['fulfillment_model'].map({'model_1': 1, 'model_2': 0})
  return data


#------------------- FEATURES
# Count distinct departments
def _count_departments(data_items):
  # create table of trip_id/count_departments
  count_department = pd.pivot_table(data_items, index = ['trip_id', 'department_name'])
  count_department.reset_index(drop = False, inplace = True)
  count_department = pd.pivot_table(count_department, index = 'trip_id', aggfunc = 'count')['department_name']
  count_department_df = pd.DataFrame(count_department)
  count_department_df.rename(columns={'department_name': 'department_count'}, inplace=True)
  return count_department_df


# Count all number of items
def _items_count(data_items):
  items_counts = pd.pivot_table(data_items, index = 'trip_id', values = 'quantity', aggfunc = 'sum')
  items_counts_df = pd.DataFrame(items_counts)
  return items_counts_df


## Categorization of shoppers
def _group_shoppers_duration(time):
  if time < 500:
      return '<500'
  elif time < 1000:
      return '<1000'
  elif time < 1500:
      return '<1500'
  elif time < 2000:
      return '<2000'
  elif time < 2500:
      return '<2500'
  elif time < 3000:
      return '<3000'
  elif time < 3500:
      return '<3500'
  elif time < 4000:
      return '<4000'
  elif time < 4500:
      return '<4500'
  elif time < 5000:
      return '<5000'
  elif time < 5500:
      return '<5500'
  else:
      return '>5500'

def _categorization_shoppers(data_raw):
  # Compute shopping time
  data_categ_shoppers = _compute_shopping_time(data_raw)
  # Pivot to get average shopping time
  average_shopping_time = pd.pivot_table(data_categ_shoppers, index = 'shopper_id', values = 'trip_length', aggfunc = 'mean')
  # Build groups
  grouping_shoppers = average_shopping_time.map(_group_shoppers_duration)
  # Turn in to data frame
  grouping_shoppers = pd.DataFrame(grouping_shoppers)
  # rename
  grouping_shoppers.columns = ['shopper_efficiency']
  return grouping_shoppers








