#!/usr/bin/env python
# coding: utf-8

# #Video Game Data Analysis

# The data from the ESRB will be analyzed in this notebook. After analysis is completed, it will be clearer which games succeeded and which did not. Also, it will help with advertising for the sales of video games next year.

# In[46]:


import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st


# In[47]:


df_games = pd.read_csv('moved_games.csv')
display(df_games.info())


# In[48]:


display(df_games.head(5))


# In[49]:


display(df_games.columns)


# In[50]:


df_games = df_games.rename(
    columns={'Name':'name',
             'Platform':'platform',
             'Year_of_Release':'year_of_release',
             'Genre':'genre',
             'NA_sales':'na_sales',
             "EU_sales":'eu_sales',
             'JP_sales':'jp_sales',
             'Other_sales':'other_sales',
             'Critic_Score':'critic_score',
             'User_Score':'user_score',
             'Rating':'rating'})
display(df_games.columns)


# In[51]:


display(df_games['user_score'].unique())
display(df_games['critic_score'].unique())


# This cell will first fill empty cells with appropriate default values. Then, the year_of_release column will be changed to integers since years are not used with decimals. The user_score column should be floats, and scores with 'tbd' should be marked with the median score. This ensures the remaining data will not appear skewed and confuse others when analyzing the data later. The critic_score will be changed to integers because all scores given by critics always end in .0 meaning no decimals were used originally.

# In[52]:


df_games['year_of_release'] = df_games['year_of_release'].fillna(-1)
df_games['rating'] = df_games['rating'].fillna('Unknown')
df_games['critic_score'] = df_games['critic_score'].fillna(df_games['critic_score'].median())
df_games['genre'] = df_games['genre'].fillna('Unknown')


# In[53]:


df_games['user_score'] = df_games['user_score'].replace(to_replace='tbd',value=df_games['critic_score'].median())
df_games['user_score'] = df_games['user_score'].fillna(df_games['critic_score'].median())
df_games['user_score'] = df_games['user_score'].astype('float64')


# In[54]:


df_games['year_of_release'] = df_games['year_of_release'].astype('int64')
df_games['critic_score'] = df_games['critic_score'].astype('int64')
df_games['user_score'] = df_games['user_score'].astype('float64')


# In[55]:


display(df_games['user_score'].sort_values().unique())
display(df_games['critic_score'].sort_values().unique())
display(df_games['year_of_release'].sort_values().unique())


# In[56]:


display(df_games.info())


# In[57]:


display(df_games.head(10))


# In[58]:


df_games['total_sales'] = df_games['na_sales'] + df_games['eu_sales'] + df_games['jp_sales'] + df_games['other_sales']
display(df_games.head(10))


# Now that the empty cells have been filled, it is time to search for duplicate games. I will search for obvious duplicates first, and then implicit duplicates after. The duplicates will all be from the name of the games being played on the same console.

# In[59]:


display(df_games[(df_games.duplicated())])


# No obvious duplicates. Now, it's time to search for implicit duplicates by printing duplicate names and seeing if they come from the same console.

# In[60]:


df_duplicate_games = df_games[df_games['name'].duplicated()]
df_duplicate_games = df_duplicate_games.groupby(['name','platform']).count().sort_values(by='genre',ascending=False)
display(df_duplicate_games.head(10))


# Three games have possible implicit duplicates: Need for Speed: Most Wanted, Madden NFL 13, and Sonic the Hedgehog. These implicit duplicates need to be removed. All sales from the duplicate value will be added to the original to ensure no lost sales counts in the data.

# In[61]:


display(df_games[df_games['name']=='Need for Speed: Most Wanted'])
display(df_games[df_games['name']=='Madden NFL 13'])
display(df_games[df_games['name']=='Sonic the Hedgehog'])


# Need for Speed actually does not have any duplicates to be removed. The game was released in 2005 and 2012 on several different consoles. Madden and Sonic both have duplicate postings on the PS3. The dupicates will now be removed and the sales from the duplicate post will be added to the original.

# In[62]:


df_games.loc[(df_games['name'] == 'Madden NFL 13') & (df_games['eu_sales'] == 0.22),'eu_sales'] = 0.23
df_games.loc[(df_games['name'] == 'Sonic the Hedgehog') & (df_games['eu_sales'] == 0.06),'eu_sales'] = 0.54
df_games.drop(4127,inplace=True)
df_games.drop(16230,inplace=True)


# In[63]:


display(df_games[df_games['name']=='Madden NFL 13'])
display(df_games[df_games['name']=='Sonic the Hedgehog'])


# Now that all duplicates have been removed from the DataFrame, it's time to start building the streamlit app. I will give the app a table sorted by console since companies and players compare their games by the consoles played on. Then, I will also build scatterplots that will help show correlation between scores by critics or users, and resulting sales. If there is a correlation anywhere, this will help the companies determine who should be impressed, and how to better advertise their upcoming games.

# In[64]:


st.header('Video Game Sales')
st.write('''
         Filter the data by platform to see the data of many video games and their popularity and sales.
         ''')


# In[65]:


platform_choice = df_games['platform'].unique()


# In[66]:


make_choice_platform = st.selectbox('Select Platform:',platform_choice)


# In[67]:


min_year,max_year = (df_games['year_of_release'].min() , df_games['year_of_release'].max())
year_range = st.slider(label='Choose year',step=int(1),min_value=int(min_year),max_value=int(max_year),value=(int(min_year),int(max_year)))


# In[68]:


actual_range = list(range(year_range[0],year_range[1]+1))


# In[69]:


filtered_type = df_games[(df_games['platform']==make_choice_platform) & (df_games['year_of_release'].isin(list(actual_range)))]
st.table(filtered_type.head(10))


# In[70]:


st.header('Game Success Analysis')
st.write("""
Let's see what influences the success of a game the most. We will compare total sales to user_score, critic_score, genre and rating.""")


# In[73]:


import plotly.express as px

list_for_histogram = ['genre','critic_score','user_score','rating']
choice_for_histogram = st.selectbox('Game Distribution Characteristic',list_for_histogram)
histogram_1 = px.histogram(df_games , x='total_sales' , color=choice_for_histogram)
histogram_1.update_layout(title="<b> Game Popularity Choice by {}<b>".format(choice_for_histogram))
st.plotly_chart(histogram_1)


# In[76]:


list_for_scatter = ['genre','critic_score','user_score','rating']
choice_for_scatter = st.selectbox('Game success dependency on ',list_for_scatter)
scatter = px.scatter(df_games , x='total_sales' , y=choice_for_scatter , hover_data=['year_of_release'])
scatter.update_layout(title="<b> Price vs {}<b>".format(choice_for_scatter))
st.plotly_chart(scatter)

