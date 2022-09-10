# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 00:42:24 2022

@author: Jordi Garcia Ruspira
"""

from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import requests
import json
import textwrap
import time
import streamlit.components.v1 as components
import requests
from matplotlib import pyplot as plt
from  matplotlib.ticker import FuncFormatter
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components
from matplotlib import pyplot as plt
from  matplotlib.ticker import FuncFormatter
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from shroomdk import ShroomDK
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

import seaborn as sns 
st.set_page_config(layout="wide")


st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 90%;
        padding-top: 5rem;
        padding-right: 5rem;
        padding-left: 5rem;
        padding-bottom: 5rem;
    }}
    img{{
    	max-width:40%;
    	margin-bottom:40px;
    }}
</style>
""",
        unsafe_allow_html=True,
    )
 

st.markdown("# Miners in Ethereum")
st.sidebar.markdown("# Kurama")
st.sidebar.success("Hi! This is a simple version :) ")
 
 
API_KEY = "3b5afbf4-3004-433c-9b04-2e867026718b"

 


SQL_QUERY_AUX = "select miner, difficulty, tx_count, size from  ethereum.core.fact_blocks where block_timestamp between '2022-01-01' and CURRENT_DATE     and miner in ('" 

SQL_QUERY_2 = "select tx_count, count(distinct block_number) as num_blocks from   ethereum.core.fact_blocks where to_date(block_timestamp) between  '2022-01-01'and current_date AND TX_COUNT > 0  group by  tx_count" 


SQL_QUERY_3 = "select to_date(block_timestamp) as date, avg(difficulty) as avg_difficulty  from   ethereum.core.fact_blocks where to_date(block_timestamp) between  '2022-01-01'and current_date AND TX_COUNT > 0  group by  date" 
   

SQL_QUERY_4 = "select miner, count(distinct block_number) as num_blocks_mined, avg(difficulty) as average_difficulty, avg(tx_count) as avg_tx_count, RANK() OVER (ORDER BY num_blocks_mined desc) as rank_num_blocks,  RANK() OVER (ORDER BY average_difficulty desc) as rank_average_difficulty, RANK() OVER (ORDER BY avg_tx_count desc) as rank_avg_tx_count from   ethereum.core.fact_blocks where to_date(block_timestamp) between  '2022-01-01'and current_date  group by  miner"

#nanopool and okex

TTL_MINUTES = 15
# return up to 100,000 results per GET request on the query id
PAGE_SIZE = 100000
# return results of page 1
PAGE_NUMBER_1 = 1 

def create_query():
    r = requests.post(
        'https://node-api.flipsidecrypto.com/queries', 
        data=json.dumps({
            "sql": SQL_QUERY2,
            "ttlMinutes": TTL_MINUTES
        }),
        headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
    )
    if r.status_code != 200:
        raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))
    
    return json.loads(r.text)    
 

def create_query2():
    r = requests.post(
        'https://node-api.flipsidecrypto.com/queries', 
        data=json.dumps({
            "sql": SQL_QUERY_2,
            "ttlMinutes": TTL_MINUTES
        }),
        headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
    )
    if r.status_code != 200:
        raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))
    
    return json.loads(r.text)    
 
 

def create_query3():
    r = requests.post(
        'https://node-api.flipsidecrypto.com/queries', 
        data=json.dumps({
            "sql": SQL_QUERY_3,
            "ttlMinutes": TTL_MINUTES
        }),
        headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
    )
    if r.status_code != 200:
        raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))
    
    return json.loads(r.text)    
  
def create_query4():
    r = requests.post(
        'https://node-api.flipsidecrypto.com/queries', 
        data=json.dumps({
            "sql": SQL_QUERY_4,
            "ttlMinutes": TTL_MINUTES
        }),
        headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
    )
    if r.status_code != 200:
        raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))
    
    return json.loads(r.text)    
  


def get_query_results(token):
    r = requests.get(
        'https://node-api.flipsidecrypto.com/queries/{token}?pageNumber={page_number}&pageSize={page_size}'.format(
          token=token,
          page_number=PAGE_NUMBER_1,
          page_size=PAGE_SIZE
        ),
        headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY}
    )
    if r.status_code != 200:
        raise Exception("Error getting query results, got response: " + r.text + "with status code: " + str(r.status_code))
    
    data = json.loads(r.text)
    if data['status'] == 'running':
        time.sleep(10)
        return get_query_results(token)

    return data

    
   

with st.container():
    st.title('Flash Bounty: Miners (Powered by FlipsideCrypto ShroomDK)')
with st.container():
    st.text("")
    st.subheader('Streamlit App by [Jordi R.](https://twitter.com/RuspiTorpi/)')

with st.container():
   
    st.markdown("In this dashboard we'll explore the main insights we can observe regarding miners behavior when it comes to transaction count per block and block difficulty.")
    st.text("")
    st.markdown("For starters, the time period defined (by myself) for this bounty has been since start of 2022, which I consider to be a sufficiently relevant time period to display the data.")
    st.text("")

    st.markdown('First things first: what do we define as high or low transaction count? In order to have a better understanding, we can plot the transaction count distribution per number of blocks, as shown in the following chart.')    
    
   
    sns.set(rc={'figure.figsize':(11.7,8.27)}, font_scale=4)
     
    query = create_query2()
    token = query.get('token')
    data1 = get_query_results(token)
    df1 = pd.DataFrame(data1['results'], columns = ['TX_COUNT','NUM_BLOCKS']) 
    df1 = df1.sort_values(by="TX_COUNT")
    
    
    
   
    plt.figure(figsize=(10, 10))
    fig = px.line(df1, x="TX_COUNT", y="NUM_BLOCKS")  
    fig.update_layout(title='Number of blocks by transaction count per block',
                   xaxis_title='Transaction count per block',
                   yaxis_title='Number of blocks')    
    st.plotly_chart(fig, use_container_width=True)
    
    
    
    
    st.markdown('We can thus see that most of the blocks have between 1 and 400 transactions, and the rest seem to be more outliers')    
     
    st.markdown('Next, we can also plot for context the average difficulty per block, where we see a drop in difficulty during July.')    
    
   
    query = create_query3()
    token = query.get('token')
    data1 = get_query_results(token)
    df1 = pd.DataFrame(data1['results'], columns = ['DATE','AVG_DIFFICULTY']) 
    df1 = df1.sort_values(by="DATE")
    
    plt.figure(figsize=(10, 10))
    fig = px.line(df1, x="DATE", y="AVG_DIFFICULTY")     
    
    fig.update_layout(title='Daily average difficulty',
                   xaxis_title='Date',
                   yaxis_title='Average difficulty')
    st.plotly_chart(fig, use_container_width=True)
    
 
    st.subheader('User selection')
    st.markdown('In this part of the dashboard, you can type two inputs of miner addresses and it will compare them automatically.')    
    st.markdown('For instance, we can use violin plots to show their difficulty distribution and transaction count per block distribution. Violin plots have many of the same summary statistics as box plots:')    
    st.markdown('* The center horizontal line represents the median')
    st.markdown('* The center horizontal **dashed** line represents the mean')
    st.markdown('* The thin line represents the rest of the distribution, except for points that are determined to be “outliers” using a method that is a function of the interquartile range.')
    st.markdown('On each side of gray line and box is a kernel density estimation to show the distribution shape of the data. Wider sections of the violin plot represent a higher probability that members of the population will take on the given value; the skinnier sections represent a lower probability.')
    
    
    input_feature = st.text_input('Introduce name of miner 1','0xea674fdde714fd979de3edf0f56aa9716b898ec8')
    input_feature_2 = st.text_input('Introduce name of miner 2','0x1ad91ee08f21be3de0ba2ba6918e714da6b45836')
    SQL_QUERY2 = SQL_QUERY_AUX+ input_feature + "','" + input_feature_2 + "')"  
    
      
    query = create_query()
    token = query.get('token')
    data1 = get_query_results(token)
    df1 = pd.DataFrame(data1['results'], columns = ['MINER','DIFFICULTY','TX_COUNT','SIZE']) 
    
    
 
     
    fig = go.Figure(data=go.Violin(y=df1['TX_COUNT'][df1['MINER'] == input_feature], box_visible=True, line_color='black',
                               meanline_visible=True, fillcolor='lightseagreen', opacity=0.6,
                               x0=input_feature))
    fig.update_layout(height=600, width=800, yaxis_zeroline=False, title="Plot Title",     xaxis_title="X Axis Title",     yaxis_title="Y Axis Title")
    st.plotly_chart(fig)
    
    
    fig = go.Figure(data=go.Violin(y=df1['TX_COUNT'][df1['MINER'] == input_feature_2], box_visible=True, line_color='black',
                               meanline_visible=True, fillcolor='lightseagreen', opacity=0.6,
                               x0=input_feature_2))
    fig.update_layout(height=600, width=800, yaxis_zeroline=False, title="Plot Title",
    xaxis_title="X Axis Title",
    yaxis_title="Y Axis Title")
    st.plotly_chart(fig)
       
    
    fig = go.Figure(data=go.Violin(y=df1['DIFFICULTY'][df1['MINER'] == input_feature], box_visible=True, line_color='black',
                               meanline_visible=True, fillcolor='lightseagreen', opacity=0.6,
                               x0=input_feature))
    fig.update_layout(height=600, width=800, yaxis_zeroline=False, title="Plot Title",     xaxis_title="X Axis Title",     yaxis_title="Y Axis Title")
    st.plotly_chart(fig)
    
    
    fig = go.Figure(data=go.Violin(y=df1['DIFFICULTY'][df1['MINER'] == input_feature_2], box_visible=True, line_color='black',
                               meanline_visible=True, fillcolor='lightseagreen', opacity=0.6,
                               x0=input_feature_2))
    fig.update_layout(height=600, width=800, yaxis_zeroline=False, title="Plot Title",
    xaxis_title="X Axis Title",
    yaxis_title="Y Axis Title")
    st.plotly_chart(fig)
    
    
    
    query = create_query4()
    token = query.get('token')
    data1 = get_query_results(token)
    df1 = pd.DataFrame(data1['results'], columns = ['MINER','NUM_BLOCKS_MINED','AVERAGE_DIFFICULTY','AVG_TX_COUNT','RANK_NUM_BLOCKS','RANK_AVERAGE_DIFFICULTY','RANK_AVG_TX_COUNT']  ) 
     
    st.dataframe(df1)
    
    rank_nblocks_miner_input_1 = df1['RANK_NUM_BLOCKS'][df1['MINER'] == input_feature ]
    dfaux = pd.DataFrame(data = rank_nblocks_miner_input_1)  
    rank_avgdif_miner_input_1 = df1['RANK_AVERAGE_DIFFICULTY'][df1['MINER'] == input_feature ]
    dfaux2 = pd.DataFrame(data = rank_avgdif_miner_input_1)  
    rank_avgtx_miner_input_1 = df1['RANK_AVG_TX_COUNT'][df1['MINER'] == input_feature ]
    dfaux3 = pd.DataFrame(data = rank_avgtx_miner_input_1)   
    
    
    
    rank_nblocks_miner_input_2 = df1['RANK_NUM_BLOCKS'][df1['MINER'] == input_feature_2 ]
    dfauxx = pd.DataFrame(data = rank_nblocks_miner_input_2)  
    rank_avgdif_miner_input_2 = df1['RANK_AVERAGE_DIFFICULTY'][df1['MINER'] == input_feature_2 ]
    dfauxx2 = pd.DataFrame(data = rank_avgdif_miner_input_2)  
    rank_avgtx_miner_input_2 = df1['RANK_AVG_TX_COUNT'][df1['MINER'] == input_feature_2 ]
    dfauxx3 = pd.DataFrame(data = rank_avgtx_miner_input_2)       
    
    
    
    
    rank_nblocks_miner_input_1_avgtx = df1['AVG_TX_COUNT'][df1['MINER'] == input_feature ]
    dfauxx4 = pd.DataFrame(data = rank_nblocks_miner_input_1_avgtx)   
    rank_nblocks_miner_input_1_numblocks = df1['NUM_BLOCKS_MINED'][df1['MINER'] == input_feature ]
    dfauxx5 = pd.DataFrame(data = rank_nblocks_miner_input_1_numblocks)   
    rank_nblocks_miner_input_1_avgdiff = df1['AVERAGE_DIFFICULTY'][df1['MINER'] == input_feature ]
    dfauxx6 = pd.DataFrame(data = rank_nblocks_miner_input_1_avgdiff)   

    rank_nblocks_miner_input_2_avgtx = df1['AVG_TX_COUNT'][df1['MINER'] == input_feature_2 ]
    dfauxx7 = pd.DataFrame(data = rank_nblocks_miner_input_2_avgtx)   
    rank_nblocks_miner_input_2_numblocks = df1['NUM_BLOCKS_MINED'][df1['MINER'] == input_feature_2 ]
    dfauxx8 = pd.DataFrame(data = rank_nblocks_miner_input_2_numblocks)   
    rank_nblocks_miner_input_2_avgdiff = df1['AVERAGE_DIFFICULTY'][df1['MINER'] == input_feature_2 ]
    dfauxx9 = pd.DataFrame(data = rank_nblocks_miner_input_2_avgdiff)     
    
    
    print1 = "Your selected miner 1 " + input_feature + " has rank " + str(dfaux.iloc[0,0]) +" when it comes to blocks mined throughout 2022, with a total number of blocks mined being " + str(dfauxx5.iloc[0,0]) + "."
    print2 = "Your selected miner 1 " + input_feature + " has rank " + str(dfaux2.iloc[0,0]) +" when it comes to average difficulty mined throughout 2022, with an average difficulty being " + str(dfauxx6.iloc[0,0]) + "."
    print3 = "Your selected miner 1 " + input_feature + " has rank " + str(dfaux3.iloc[0,0]) +" when it comes to average transaction count per block throughout 2022, with an average transaction per block being " + str(dfauxx4.iloc[0,0])     + "."
    print11 = "Your selected miner 2 " + input_feature_2 + " has rank " + str(dfauxx.iloc[0,0]) +" when it comes to blocks mined throughout 2022, with a total number of blocks mined being " + str(dfauxx8.iloc[0,0]) + "."
    print22 = "Your selected miner 2 " + input_feature_2 + " has rank " + str(dfauxx2.iloc[0,0]) +" when it comes to average difficulty mined throughout 2022, with an average difficulty being " + str(dfauxx9.iloc[0,0]) + "."
    print33 = "Your selected miner 2 " + input_feature_2 + " has rank " + str(dfauxx3.iloc[0,0]) +" when it comes to average transaction count per block mined throughout 2022, with an average transaction per block being " + str(dfauxx7.iloc[0,0])  + "."
    
    st.markdown(print1)
    st.markdown(print2)
    st.markdown(print3)
    st.markdown(print11)
    st.markdown(print22)
    st.markdown(print33)
        
