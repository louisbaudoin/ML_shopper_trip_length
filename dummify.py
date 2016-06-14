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

## Dummify function to add features depending on values (ex: fulfillment_model)
def dummify(data, column):
  data_column = data[column]
  dumm = pd.get_dummies(data_column, prefix = column, prefix_sep = '_')
  data = data.merge(dumm, left_index = True, right_index = True, how ='left')
  del data[column]
  return data
