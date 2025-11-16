#!/usr/bin/env python
# coding: utf-8

# # Final

# In[23]:


import yahoo_fin.stock_info as si
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import pyfolio as pf
from IPython.display import display


# In[20]:


import requests
import bs4 as bs

def get_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    tickers = sorted([x[:-1].lstrip().rstrip() for x in tickers])
    return tickers


# In[44]:


def getsummary(ticker):
    # table = si.get_quote_table(ticker, dict_result = False)
    table_info = {
        "key": [],
        "value": [],
    }

    stock = yf.Ticker(ticker)

    table_info["key"].append("Previous Close")
    table_info["value"].append(stock.info["previousClose"])
    table_info["key"].append("Open")
    table_info["value"].append(stock.info["open"])
    table_info["key"].append("Bid")
    table_info["value"].append(stock.info["bid"])
    table_info["key"].append("Ask")
    table_info["value"].append(stock.info["ask"])


    table = pd.DataFrame(table_info)
    return table 

# getsummary('MSFT')


# In[49]:


def getstockdata(ticker):
    stockdata = yf.download(ticker, period = 'MAX')
    return stockdata

# getstockdata("AAPL")


# In[88]:


def getanalysis(ticker):
    analysts_site = "https://finance.yahoo.com/quote/"+ ticker +"/analysis"
    headers = {'User-agent': 'Mozilla/5.0'}
    tables = pd.read_html(requests.get(analysts_site, headers=headers).text)
    table_names = ["Earnings Estimate", 
                   "Revenue Estimate", 
                   "Earnings History",
                   "EPS Trend", 
                   "EPS Revisions",
                   "Growth Estimates"]
    table_mapper = {key : val for key , val in zip(table_names , tables[:len(table_names)])}
    analysis_dict = table_mapper
    return analysis_dict.items()


# ## Tab 1

# In[24]:


tickers_list = ['-'] + get_sp500_tickers() # si.tickers_sp500()
display(tickers_list[:5])


# In[45]:


ticker = "AAPL"


# In[46]:


# Lấy thông tin cổ phiếu
getsummary(ticker)


# In[51]:


# Vẽ đồ thị
chartdata = getstockdata(ticker) 
fig = px.area(chartdata, chartdata.index, chartdata['Close'])


# In[52]:


fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=3, label="3Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(label = "MAX", step="all")
                ])
            )
        )


# ## Tab 5

# In[100]:


stock = yf.Ticker("AAPL")


# In[ ]:


ticker = "AAPL"


# In[97]:


analysis = getanalysis(ticker)
print(len(analysis))
for i in range(len(analysis)):
    name = list(analysis)[i][0]
    df = pd.DataFrame(list(analysis)[i][1])
    display(name)
    display(df)


# In[65]:


analysis = getanalysis(ticker)
for i in range(6):
    df = pd.DataFrame(list(analysis)[i][1])
    display(df)


# In[61]:





# 

# # End
