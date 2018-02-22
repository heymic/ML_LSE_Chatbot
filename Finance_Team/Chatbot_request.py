# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator
import matplotlib.dates as mdates


import seaborn as sns
sns.reset_orig() # don't change the style of plots

import glob
import datetime
import dateutil.parser

### Changing working directory...
path = r"C:\Users\heyde\Documents\01 - Master Degree\ML Society\ML_LSE_Chatbot\Finance_Team"
os.chdir(path)
cwd = os.getcwd()

## CSV Files
csv_files = glob.glob('nyse\*.csv')
csv_files

## Preliminiary Code


def read_stock_price_data():
    '''Reads in the stock_price dataframe adjusted for stock splits'''
    csv_files = glob.glob('nyse\*.csv')
    csv_files
    stock_price_df = pd.read_csv(csv_files[1], parse_dates = ['date'])
    return stock_price_df

def get_price_wide():
    '''Returns the Price dataframe in wide format with the corresponding dates'''
    stock_price_df = read_stock_price_data()
    prices_df = stock_price_df[['symbol','close', 'date']].sort_values(['symbol', 'date'])
    prices_df = prices_df.pivot_table(index = 'date', columns = 'symbol', values = 'close')
    prices_df.reset_index(inplace=True)
    prices_dates = prices_df['date']
    prices_df.drop('date', inplace = True, axis = 1)
    return prices_df, prices_dates

def get_returns():
    '''Return data wuth logarithmic returns'''
    prices_df, prices_dates = get_price_long()
    return_daily_df = prices_df.apply(lambda x: np.log(x) - np.log(x.shift(1))) # shift moves dates back by 1.
    return_daily_df.set_index(prices_dates, inplace = True)
    return return_daily_df


def stock_price_on_day(stock_symbol, datestring, DF = read_stock_price_data(), firstTime = "1"):
    ''' this function returns the latest available data when asked for a single day
    it gives a tuple with the dataframe with the data and a commend specifying the date 
    to draw the user's attention'''
    if firstTime == "1":
        global input_date
        input_date = (datestring +'.')[:-1]; #hack to copy a string..
    date = dateutil.parser.parse(datestring, dayfirst = True)
    ## code to say that date need to be between 2010-01-01 to 2016-12-30 -> raiseError if?, assert(??)    
    on_day_df = DF.loc[(DF['symbol'] == stock_symbol) & (DF['date'] == date)]
    if on_day_df.empty:
        new_date = date - datetime.timedelta(days = 1)
        new_date = new_date.strftime('%d/%m/%Y')
        return DF(stock_symbol, new_date, DF, "2")
    else:
        #comm = "showing latest available data for " + datestring
        print("The last available data for " + input_date + " is " + datestring)
        return on_day_df
    
def stock_price_on_range(stock_symbol, date_start, date_end, DF = read_stock_price_data()): 
    '''This function returns a dataframe of prices for a specified range of dates'''
    date_start = dateutil.parser.parse(date_start, dayfirst = True)
    date_end = dateutil.parser.parse(date_end, dayfirst = True)
    dates = pd.date_range(start=date_start, end=date_end, freq='D')
    ## code to say that date need to be between 2010-01-01 to 2016-12-30 -> raiseError if?, assert(??)
    prices_on_range_df = DF(stock_symbol, dates[0].strftime('%d/%m/%Y'))
    for i in range(1, len(dates)):
        next_date_df = DF('NFLX', dates[i].strftime('%d/%m/%Y'))
        prices_on_range_df = prices_on_range_df.append(next_date_df)
    return prices_on_range_df


