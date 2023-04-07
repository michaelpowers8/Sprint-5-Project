#!/usr/bin/env python
# coding: utf-8

# # Video Game Data Analysis

# The data from the ESRB will be analyzed in this notebook. After analysis is completed, it will be clearer which games succeeded and which did not. Also, it will help with advertising for the sales of video games next year.

# ## Preprocessing

# ### Initialization

# In[293]:


import pandas as pd
#import streamlit as st
from matplotlib import pyplot as plt
from scipy import stats
import numpy as np
import random
import math


# ### Load Data 

# In[294]:


df_games = pd.read_csv('moved_games.csv')


# ### Preparing Data

# In[295]:


display(df_games.info())
display(df_games.head(5))


# In[296]:


display(df_games.columns)


# In[297]:


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


# In[298]:


display(df_games['user_score'].unique())
display(df_games['critic_score'].unique())


# This cell will first fill empty cells with appropriate default values. Then, the year_of_release column will be changed to integers since years are not used with decimals. The user_score column should be floats, and scores with 'tbd' should be marked with the median score. This ensures the remaining data will not appear skewed and confuse others when analyzing the data later. The critic_score will be changed to integers because all scores given by critics always end in .0 meaning no decimals were used originally.

# In[299]:


df_games['year_of_release'] = df_games['year_of_release'].fillna(df_games['year_of_release'].median())
df_games['rating'] = df_games['rating'].fillna('Unknown')
df_games['critic_score'] = df_games['critic_score'].fillna(df_games['critic_score'].median())
df_games['genre'] = df_games['genre'].fillna('Unknown')


# In[300]:


df_games['user_score'] = df_games['user_score'].replace(to_replace='tbd',value=None)
df_games['user_score'] = df_games['user_score'].fillna(df_games['user_score'].median())
df_games['user_score'] = df_games['user_score'].astype('float64')


# In[301]:


df_games['year_of_release'] = df_games['year_of_release'].astype('int64')
df_games['critic_score'] = df_games['critic_score'].astype('int64')
df_games['user_score'] = df_games['user_score'].astype('float64')


# In[302]:


display(df_games['user_score'].sort_values().unique())
display(df_games['critic_score'].sort_values().unique())
display(df_games['year_of_release'].sort_values().unique())


# In[303]:


display(df_games.info())


# In[304]:


display(df_games.head(10))


# ### Duplicates

# Now that the empty cells have been filled, it is time to search for duplicate games. I will search for obvious duplicates first, and then implicit duplicates after. The duplicates will all be from the name of the games being played on the same console.

# In[305]:


display(df_games[(df_games.duplicated())])


# No obvious duplicates. Now, it's time to search for implicit duplicates by printing duplicate names and seeing if they come from the same console.

# In[306]:


df_duplicate_games = df_games[df_games['name'].duplicated()]
df_duplicate_games = df_duplicate_games.groupby(['name','platform']).count().sort_values(by='genre',ascending=False)
display(df_duplicate_games.head(10))


# Three games have possible implicit duplicates: Need for Speed: Most Wanted, Madden NFL 13, and Sonic the Hedgehog. These implicit duplicates need to be removed. All sales from the duplicate value will be added to the original to ensure no lost sales counts in the data.

# In[307]:


display(df_games[df_games['name']=='Need for Speed: Most Wanted'])
display(df_games[df_games['name']=='Madden NFL 13'])
display(df_games[df_games['name']=='Sonic the Hedgehog'])


# Need for Speed actually does not have any duplicates to be removed. The game was released in 2005 and 2012 on several different consoles. Madden and Sonic both have duplicate postings on the PS3. The dupicates will now be removed and the sales from the duplicate post will be added to the original.

# In[308]:


df_games.loc[(df_games['name'] == 'Madden NFL 13') & (df_games['eu_sales'] == 0.22),'eu_sales'] = 0.23
df_games.loc[(df_games['name'] == 'Sonic the Hedgehog') & (df_games['eu_sales'] == 0.06),'eu_sales'] = 0.54
df_games.drop(4127,inplace=True)
df_games.drop(16230,inplace=True)


# In[309]:


display(df_games[df_games['name']=='Madden NFL 13'])
display(df_games[df_games['name']=='Sonic the Hedgehog'])


# ### Enrichment

# Now that all duplicates have been removed from the DataFrame, it is time to start enriching the data. Start with finding the total sales of each game and creating a new column in the DataFrame for it.

# In[310]:


df_games['total_sales'] = df_games['na_sales'] + df_games['eu_sales'] + df_games['jp_sales'] + df_games['other_sales']
display(df_games.head(10))


# ## Comparing Platform Sales 

# ### Most Popular Platform

# In[311]:


platform_sales = []
platform_choice = df_games['platform'].unique()
for platform in platform_choice:
    platform_sales.append([platform,round(df_games[(df_games['platform']==platform)]['total_sales'].sum(),2)])
display(platform_sales)


# The PS2 had the most total sales next to every other platform in this dataset. Now it is time to build distributions on the PS2 data to see when they were popular, and use their primetime years to evaluate how and why they were so successful.

# In[312]:


ps2_games = df_games[(df_games['platform']=='PS2')]
display(ps2_games.head())


# ### Specifying Timeline

# In[313]:


display(ps2_games.groupby('year_of_release')['name'].count())


# Based on the ps2 data by year, the platform was creating games from 2000-2011. This is the time period I will be focusing on to further analyze the data.

# In[314]:


relevant_games = df_games[(df_games['year_of_release'] >= 2000) & (df_games['year_of_release'] <= 2011)]


# In[315]:


display(relevant_games.groupby('platform')['total_sales'].sum())


# In this timeframe, besides the PS2, the DS, Wii, and XBOX 360 are leading in sales. The PS3 is not too far behind. Let's see which of these are growing, and which are shrinking.

# In[316]:


for popular_platform in ['PS2','X360','PS3','Wii','DS','GBA']:
    relevant_games[relevant_games['platform']==popular_platform].groupby('year_of_release')['total_sales'].sum().plot()
plt.legend(['PS2','X360','PS3','Wii','DS','GBA'])
plt.show()


# In this timeframe, we saw the ps2 rise and fall, along with the DS, and even the Wii. The XBOX 360 was still high and it is inconclusive if it was falling, or if it just had a slow year. With the fall of the PS2, it was clear that the rise of the PS3 was underway. A very successful platform maybe has a lifespan of popularity of about 10 years. An average platform seems to rise and fall in about 6-7 years.

# In[317]:


data = []
for platform in relevant_games['platform'].unique():
    data.append(relevant_games[relevant_games['platform']==platform].groupby('year_of_release')['total_sales'].sum())
plt.boxplot(data,vert=False,showfliers=True,labels=relevant_games['platform'].unique())
plt.show()


# The difference in sales is very significant between platforms. The most popular platforms have median yearly total sales over triple the less popular platforms. For the largest platforms, their yearly sales were around 120, and the other platforms had yearly sales around 40 or less. Given the timeframe covers the entire existence of the ps2, it has the widest range of yearly sales. On the opposite side, a platform like the 2600 only has data from one year, 2007, in this entire timeframe. Therefore, its range is just one value. The most competitive platforms in this timeframe to the PS2, besides the PS3 since they are the same company, was the XBOX 360, DS, and Wii. 

# ### Other Popular Platform

# I will now take a closer look at the XBOX 360, my personal favorite console, and see how its sales were affected by users, and professional critics. 

# In[318]:


xbox_games = relevant_games[relevant_games['platform']=='X360']


# In[319]:


xbox_games.plot(
                kind='scatter',
                title='Sales vs Users',
                x='user_score',
                y='total_sales',
                xlabel='User Score',
                ylabel='Total Sales (USD)'
)
xbox_games.plot(
                kind='scatter',
                title='Sales vs Critics',
                x='critic_score',
                y='total_sales',
                xlabel='Critic Score',
                ylabel='Total Sales (USD)'
)


# Based on the scatterplots, there seems to be a little correlation between sales and scores of both critics and users. The effect is not noticed until the user and critic scores are in the top about 20% of scores. The exception to this general rule is the game that Nintendo geniusely included, Wii Sports. This strategy provided all new players with an immediate game and a quick boost. Time to run a quick formality of testing hypotheses on sales versus critics and users.

# Null Hypothesis: Total Sales are affected by the scores of critics, and users.

# Alternate Hypothesis: Total Sales are not affected by the scores of critics, and users.

# In[320]:


alpha = 0.05
results = stats.ttest_ind(xbox_games.groupby('year_of_release')['total_sales'].mean() , xbox_games.groupby('year_of_release')['user_score'].mean() , equal_var=True)

display('p-value:', results.pvalue)
if (results.pvalue < alpha):
    display("We reject the null hypothesis: sales were not significantly affected by user scores.")
else:
    display("We can't reject the null hypothesis: sales were significantly affected by user scores.")


# In[321]:


results = stats.ttest_ind(xbox_games.groupby('year_of_release')['total_sales'].mean() , xbox_games.groupby('year_of_release')['critic_score'].mean() , equal_var=True)

display('p-value:', results.pvalue)
if (results.pvalue < alpha):
    display("We reject the null hypothesis: sales were not significantly affected by critic scores.")
else:
    display("We can't reject the null hypothesis: sales were significantly affected by critic scores.")


# ### Multiple Platforms

# In this section, I am now going to find the games that are in the relevant timeframe of the data that are also on multiple platforms. 

# In[322]:


multiple_platforms = relevant_games.groupby('name')['platform'].nunique()


# In[323]:


multiple_platforms = relevant_games.groupby('name').agg(platforms=('platform', 'nunique'))
multiple_platform_game_names = multiple_platforms[multiple_platforms['platforms'] > 1].reset_index()['name']
relevant_multiplatform_games = relevant_games[relevant_games['name'].isin(multiple_platform_game_names)].copy()


# Now that we have the multiplatform games, it is time to compare how sales are for the games on each of their platforms separately. I am not certain on the best way to do this, so for now, I will just choose a random game from the dataframe and plot its sales per platform, and run several trials and make note of the results. 

# In[324]:


game = random.choice(relevant_multiplatform_games['name'].unique())
relevant_multiplatform_games[relevant_multiplatform_games['name']==game].sort_values(by='platform').plot(
    kind='scatter',
    x='platform',
    y='total_sales',
    title=f'{game} Sales by Platform',
    ylim=(0,relevant_multiplatform_games[relevant_multiplatform_games['name']==game]['total_sales'].sum())
)


# 

# Now it is time to compare sales by genre of games. To do this, I will make a dataframe where each column name is a genre, and the entries will be the sale totals for the games of those specific genres. Since putting in a bunch of zeros for the empty cells will skew the averages greatly and make everything seem less profitable, I will leave empty cells empty for now and just plot the existing values on boxplots side by side.

# In[325]:


for genre in relevant_multiplatform_games['genre'].unique():
    relevant_multiplatform_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['total_sales']
sales_by_genre_df = pd.DataFrame(data=relevant_multiplatform_games[['Action', 'Shooter', 'Misc', 'Role-Playing', 'Simulation', 'Sports', 'Racing', 'Platform', 'Adventure', 'Fighting', 'Puzzle', 'Strategy']],columns=relevant_multiplatform_games['genre'].unique())
relevant_multiplatform_games = relevant_multiplatform_games.drop(columns=['Action', 'Shooter', 'Misc', 'Role-Playing', 'Simulation', 'Sports', 'Racing', 'Platform', 'Adventure', 'Fighting', 'Puzzle', 'Strategy'])

display(sales_by_genre_df)


# In[326]:


display(sales_by_genre_df.sum())


# In[327]:


sales_by_genre_df[['Action', 'Shooter', 'Misc', 'Role-Playing', 'Simulation', 'Sports', 'Racing', 'Platform', 'Adventure', 'Fighting', 'Puzzle', 'Strategy']].plot(
    kind='box',
    title='Sales by Genre With Outliers',
    vert=False,
    showfliers=True
)
sales_by_genre_df[['Action', 'Shooter', 'Misc', 'Role-Playing', 'Simulation', 'Sports', 'Racing', 'Platform', 'Adventure', 'Fighting', 'Puzzle', 'Strategy']].plot(
    kind='box',
    title='Sales by Genre Without Outliers',
    vert=False,
    showfliers=False
)


# Looking at all of the genres side by side, without outliers paints a better general picture. Fighting games do better on average as the median sales is largest and even its upper and lower quartiles are higher than the other genres. However, when looking at the outliers, it can be argued that sports, action, and shooter games are the most successful. However, for these genres, if the games are not exceptional, they will not do as well.

# ## Regional Sales

# It is now time to determine the 5 most popular platforms and genres of each region and figure out if the ESRB rating affects the sales in each region. Starting with North America.

# ### North America Platforms

# In[328]:


na_relevant_games = relevant_games[relevant_games['na_sales']>0]


# In[329]:


platform_sales.clear()
for platform in platform_choice:
    platform_sales.append([platform,round(na_relevant_games[(na_relevant_games['platform']==platform)]['na_sales'].sum(),2)])
display(platform_sales)


# Based on the sales list of each platform in North America, the top 5 most popular platforms are 
# 1. PS2 
# 2. Wii
# 3. XBOX 360 
# 4. DS
# 5. PS3 
# I will now also count how many games were sold on each platform. This will ensure that the sales of very popular games do not leave the less popular games out of the picture.

# In[330]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    count = na_relevant_games[na_relevant_games['platform']==platform]['platform'].count()
    display(f'{platform}: {count}')


# Based on just number of games sold on each of the 5 platforms, the popularity ranking is:
# 1. PS2
# 2. DS
# 3. Wii
# 4. XBOX 360
# 5. PS3 
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[331]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    na_relevant_games[platform] = relevant_multiplatform_games[relevant_multiplatform_games['platform']==platform]['na_sales']
na_sales_by_platform_df = pd.DataFrame(data=na_relevant_games[['PS2','Wii','X360','DS','PS3']],columns=['PS2','Wii','X360','DS','PS3'])
na_relevant_games = na_relevant_games.drop(columns=['PS2','Wii','X360','DS','PS3'])


# In[332]:


na_sales_by_platform_df[['PS2','Wii','X360','DS','PS3']].plot(
    kind='box',
    title='Sales by Platform With Outliers',
    vert=False,
    showfliers=True
)
na_sales_by_platform_df[['PS2','Wii','X360','DS','PS3']].plot(
    kind='box',
    title='Sales by Platform Without Outliers',
    vert=False,
    showfliers=False
)


# 

# ### Europe Platforms

# In[333]:


eu_relevant_games = relevant_games[relevant_games['eu_sales']>0]


# In[334]:


platform_sales.clear()
for platform in platform_choice:
    platform_sales.append([platform,round(na_relevant_games[(na_relevant_games['platform']==platform)]['eu_sales'].sum(),2)])
display(platform_sales)


# Based on the sales list of each platform in Europe, the top 5 most popular platforms are 
# 1. PS2 
# 2. Wii
# 3. PS3 
# 4. XBOX 360
# 5. DS
# I will now also count how many games were sold on each platform. This will ensure that the sales of very popular games do not leave the less popular games out of the picture.

# In[335]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    count = eu_relevant_games[eu_relevant_games['platform']==platform]['platform'].count()
    display(f'{platform}: {count}')


# Based on just number of games sold on each of the 5 platforms, the popularity ranking is:
# 1. PS2
# 2. DS
# 3. XBOX 360
# 4. Wii
# 5. PS3
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[336]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    eu_relevant_games[platform] = relevant_multiplatform_games[relevant_multiplatform_games['platform']==platform]['eu_sales']
eu_sales_by_platform_df = pd.DataFrame(data=eu_relevant_games[['PS2','Wii','X360','DS','PS3']],columns=['PS2','Wii','X360','DS','PS3'])
eu_relevant_games = eu_relevant_games.drop(columns=['PS2','Wii','X360','DS','PS3'])


# In[337]:


eu_sales_by_platform_df[['PS2','Wii','X360','DS','PS3']].plot(
    kind='box',
    title='Sales by Platform With Outliers',
    vert=False,
    showfliers=True
)
eu_sales_by_platform_df[['PS2','Wii','X360','DS','PS3']].plot(
    kind='box',
    title='Sales by Platform Without Outliers',
    vert=False,
    showfliers=False
)


# 

# ### Japan Platforms

# In[338]:


jp_relevant_games = relevant_games[relevant_games['jp_sales']>0]


# In[339]:


platform_sales.clear()
for platform in platform_choice:
    platform_sales.append([platform,round(jp_relevant_games[(jp_relevant_games['platform']==platform)]['jp_sales'].sum(),2)])
display(platform_sales)


# Based on the sales list of each platform in Europe, the top 5 most popular platforms are 
# 1. DS 
# 2. PS2
# 3. PSP 
# 4. Wii
# 5. PS3
# I will now also count how many games were sold on each platform. This will ensure that the sales of very popular games do not leave the less popular games out of the picture.

# In[340]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    count = jp_relevant_games[jp_relevant_games['platform']==platform]['platform'].count()
    display(f'{platform}: {count}')


# Based on just number of games sold on each of the 5 platforms, the popularity ranking is:
# 1. PS2
# 2. DS
# 3. PS3
# 4. XBOX 360
# 5. Wii
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[341]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    jp_relevant_games[platform] = relevant_multiplatform_games[relevant_multiplatform_games['platform']==platform]['jp_sales']
jp_sales_by_platform_df = pd.DataFrame(data=jp_relevant_games[['PS2','Wii','X360','DS','PS3']],columns=['PS2','Wii','X360','DS','PS3'])
jp_relevant_games = jp_relevant_games.drop(columns=['PS2','Wii','X360','DS','PS3'])


# In[342]:


jp_sales_by_platform_df[['PS2','Wii','X360','DS','PS3']].plot(
    kind='box',
    title='Sales by Platform With Outliers',
    vert=False,
    showfliers=True
)
jp_sales_by_platform_df[['PS2','Wii','X360','DS','PS3']].plot(
    kind='box',
    title='Sales by Platform Without Outliers',
    vert=False,
    showfliers=False
)


# Based on the total sales in Japan, number of games sold, and sale distribution

# ### North America Genres

# In[343]:


na_relevant_games_genres_sales = []
for genre in na_relevant_games['genre'].unique():
    na_relevant_games_genres_sales.append([genre,round(na_relevant_games[(na_relevant_games['genre']==genre)]['na_sales'].sum(),2)])
display(na_relevant_games_genres_sales)


# Based on the sales list of each genre in North America, the top 5 most popular genres are 
# 1. Action 
# 2. Sports
# 3. Shooter 
# 4. Miscellaneous
# 5. Racing
# I will now also count how many games were sold in each genre. This will ensure that the sales of very popular games do not leave the less popular games out of the picture.

# In[344]:


na_relevant_games_genres_num_games = []
for genre in ['Action','Sports','Shooter','Misc','Racing']:
    na_relevant_games_genres_num_games.append([genre,na_relevant_games[(na_relevant_games['genre']==genre)]['na_sales'].count()])
display(na_relevant_games_genres_num_games)


# Based on just number of games sold in each of the 5 genres, the popularity ranking is:
# 1. Action
# 2. Sports
# 3. Miscellaneous
# 4. Racing
# 5. Shooter
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[345]:


for genre in ['Action','Sports','Shooter','Misc','Racing']:
    na_relevant_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['na_sales']
na_sales_by_genre_df = pd.DataFrame(data=na_relevant_games[['Action','Sports','Shooter','Misc','Racing']],columns=['Action','Sports','Shooter','Misc','Racing'])
na_relevant_games = na_relevant_games.drop(columns=['Action','Sports','Shooter','Misc','Racing'])


# In[346]:


na_sales_by_genre_df[['Action','Sports','Shooter','Misc','Racing']].plot(
    kind='box',
    title='Sales by Genre With Outliers',
    vert=False,
    showfliers=True
)
na_sales_by_genre_df[['Action','Sports','Shooter','Misc','Racing']].plot(
    kind='box',
    title='Sales by Genre Without Outliers',
    vert=False,
    showfliers=False
)


# ### Europe Genres

# In[347]:


eu_relevant_games_genres_sales = []
for genre in eu_relevant_games['genre'].unique():
    eu_relevant_games_genres_sales.append([genre,round(na_relevant_games[(na_relevant_games['genre']==genre)]['eu_sales'].sum(),2)])
display(eu_relevant_games_genres_sales)


# Based on the sales list of each genre in Europe, the top 5 most popular genres are 
# 1. Action 
# 2. Sports
# 3. Shooter 
# 4. Racing
# 5. Miscellaneous
# I will now also count how many games were sold in each genre. This will ensure that the sales of very popular games do not leave the less popular games out of the picture.

# In[348]:


eu_relevant_games_genres_num_games = []
for genre in ['Action','Sports','Shooter','Misc','Racing']:
    eu_relevant_games_genres_num_games.append([genre,eu_relevant_games[(eu_relevant_games['genre']==genre)]['eu_sales'].count()])
display(eu_relevant_games_genres_num_games)


# Based on just number of games sold in each of the 5 genres, the popularity ranking is:
# 1. Action
# 2. Sports
# 3. Miscellaneous
# 4. Racing
# 5. Shooter
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[349]:


for genre in ['Action','Sports','Shooter','Misc','Racing']:
    eu_relevant_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['eu_sales']
eu_sales_by_genre_df = pd.DataFrame(data=eu_relevant_games[['Action','Sports','Shooter','Misc','Racing']],columns=['Action','Sports','Shooter','Misc','Racing'])
eu_relevant_games = eu_relevant_games.drop(columns=['Action','Sports','Shooter','Misc','Racing'])


# In[350]:


eu_sales_by_genre_df[['Action','Sports','Shooter','Misc','Racing']].plot(
    kind='box',
    title='Sales by Genre With Outliers',
    vert=False,
    showfliers=True
)
eu_sales_by_genre_df[['Action','Sports','Shooter','Misc','Racing']].plot(
    kind='box',
    title='Sales by Genre Without Outliers',
    vert=False,
    showfliers=False
)


# ### Japan Genres

# In[351]:


jp_relevant_games_genres_sales = []
for genre in jp_relevant_games['genre'].unique():
    jp_relevant_games_genres_sales.append([genre,round(jp_relevant_games[(jp_relevant_games['genre']==genre)]['jp_sales'].sum(),2)])
display(jp_relevant_games_genres_sales)


# Based on the sales list of each genre in Europe, the top 5 most popular genres are 
# 1. Role-Playing 
# 2. Action
# 3. Miscellaneous 
# 4. Sports
# 5. Platform
# I will now also count how many games were sold in each genre. This will ensure that the sales of very popular games do not leave the less popular games out of the picture.

# In[352]:


jp_relevant_games_genres_num_games = []
for genre in ['Role-Playing','Action','Misc','Sports','Platform']:
    jp_relevant_games_genres_num_games.append([genre,jp_relevant_games[(jp_relevant_games['genre']==genre)]['jp_sales'].count()])
display(jp_relevant_games_genres_num_games)


# Based on just number of games sold in each of the 5 genres, the popularity ranking is:
# 1. Role-Playing
# 2. Action
# 3. Sports
# 4. Miscellaneous
# 5. Platform
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[353]:


for genre in ['Role-Playing','Action','Misc','Sports','Platform']:
    jp_relevant_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['jp_sales']
jp_sales_by_genre_df = pd.DataFrame(data=jp_relevant_games[['Role-Playing','Action','Misc','Sports','Platform']],columns=['Role-Playing','Action','Misc','Sports','Platform'])
jp_relevant_games = jp_relevant_games.drop(columns=['Role-Playing','Action','Misc','Sports','Platform'])


# In[354]:


jp_sales_by_genre_df[['Role-Playing','Action','Misc','Sports','Platform']].plot(
    kind='box',
    title='Sales by Genre With Outliers',
    vert=False,
    showfliers=True
)
jp_sales_by_genre_df[['Role-Playing','Action','Misc','Sports','Platform']].plot(
    kind='box',
    title='Sales by Genre Without Outliers',
    vert=False,
    showfliers=False
)


# ### ESRB North America

# In[355]:


na_relevant_games_rating_sales = []
for rating in na_relevant_games['rating'].unique():
    na_relevant_games_rating_sales.append([rating,round(na_relevant_games[(na_relevant_games['rating']==rating)]['na_sales'].sum(),2)])
display(na_relevant_games_rating_sales)


# Based on rating sales alone, it seems like games rated E are the most popular. Hoowever, it's likely that more games are made rated E. Let's make some boxplots to see the distribution of sales of games based on rating.

# In[356]:


for rating in ['E','Unknown','M','T','E10+','AO','EC']:
    na_relevant_games[rating] = relevant_multiplatform_games[relevant_multiplatform_games['rating']==rating]['na_sales']
na_sales_by_genre_df = pd.DataFrame(data=na_relevant_games[['E','Unknown','M','T','E10+','AO','EC']],columns=['E','Unknown','M','T','E10+','AO','EC'])
na_relevant_games = na_relevant_games.drop(columns=['E','Unknown','M','T','E10+','AO','EC'])


# In[357]:


na_sales_by_genre_df[['E','Unknown','M','T','E10+','AO','EC']].plot(
    kind='box',
    title='Sales by Rating With Outliers',
    vert=False,
    showfliers=True
)
na_sales_by_genre_df[['E','Unknown','M','T','E10+','AO','EC']].plot(
    kind='box',
    title='Sales by Rating Without Outliers',
    vert=False,
    showfliers=False
)


# ### ESRB Europe

# In[358]:


eu_relevant_games_rating_sales = []
for rating in eu_relevant_games['rating'].unique():
    eu_relevant_games_rating_sales.append([rating,round(eu_relevant_games[(eu_relevant_games['rating']==rating)]['eu_sales'].sum(),2)])
display(eu_relevant_games_rating_sales)


# In[359]:


for rating in ['E','Unknown','M','T','E10+','AO','EC']:
    eu_relevant_games[rating] = relevant_multiplatform_games[relevant_multiplatform_games['rating']==rating]['eu_sales']
eu_sales_by_genre_df = pd.DataFrame(data=eu_relevant_games[['E','Unknown','M','T','E10+','AO','EC']],columns=['E','Unknown','M','T','E10+','AO','EC'])
eu_relevant_games = eu_relevant_games.drop(columns=['E','Unknown','M','T','E10+','AO','EC'])


# In[360]:


eu_sales_by_genre_df[['E','Unknown','M','T','E10+','AO','EC']].plot(
    kind='box',
    title='Sales by Rating With Outliers',
    vert=False,
    showfliers=True
)
eu_sales_by_genre_df[['E','Unknown','M','T','E10+','AO','EC']].plot(
    kind='box',
    title='Sales by Rating Without Outliers',
    vert=False,
    showfliers=False
)


# ### ESRB Japan

# In[361]:


jp_relevant_games_rating_sales = []
for rating in na_relevant_games['rating'].unique():
    jp_relevant_games_rating_sales.append([rating,round(jp_relevant_games[(jp_relevant_games['rating']==rating)]['eu_sales'].sum(),2)])
display(jp_relevant_games_rating_sales)


# In[362]:


for rating in ['E','Unknown','M','T','E10+','AO','EC']:
    jp_relevant_games[rating] = relevant_multiplatform_games[relevant_multiplatform_games['rating']==rating]['jp_sales']
jp_sales_by_genre_df = pd.DataFrame(data=jp_relevant_games[['E','Unknown','M','T','E10+','AO','EC']],columns=['E','Unknown','M','T','E10+','AO','EC'])
jp_relevant_games = jp_relevant_games.drop(columns=['E','Unknown','M','T','E10+','AO','EC'])


# In[363]:


jp_sales_by_genre_df[['E','Unknown','M','T','E10+','AO','EC']].plot(
    kind='box',
    title='Sales by Rating With Outliers',
    vert=False,
    showfliers=True
)
jp_sales_by_genre_df[['E','Unknown','M','T','E10+','AO','EC']].plot(
    kind='box',
    title='Sales by Rating Without Outliers',
    vert=False,
    showfliers=False
)


# ## Test Hypotheses

# ### XBOX vs PC

# The user score is not affected if a game is played on the XBOX One or the PC.

# In[364]:


alpha = 0.05
results = stats.ttest_ind(relevant_games[relevant_games['platform']=='XB']['user_score'] , relevant_games[relevant_games['platform']=='PC']['user_score'] , equal_var=True)

display(f'p-value: {results.pvalue}')
if (results.pvalue < alpha):
    display("We reject the null hypothesis: user score was affected by the platform chosen.")
else:
    display("We can't reject the null hypothesis: user score was not significantly affected based on the platform.")


# ### Action vs Sports

# The user score is not affected depending on if a game is labeled 'Action' or 'Sports.'

# In[365]:


alpha = 0.05
results = stats.ttest_ind(relevant_games[relevant_games['genre']=='Action']['user_score'] , relevant_games[relevant_games['genre']=='Sports']['user_score'] , equal_var=True)

display(f'p-value: {results.pvalue}')
if (results.pvalue < alpha):
    display("We reject the null hypothesis: user score was affected by genre.")
else:
    display("We can't reject the null hypothesis: user score was not significantly affected by the genre.")


# I formulated the null hypothesis by asking myself "Does platform affect the user score?" and "Does genre affect the user score?" Then, I rephrased that question and assumed and rewrote statements that assume there is no relationship between genres, platforms, and user scores.

# The significance level I chose for these tests were 0.05 because if I am telling the company that user ratings are not affected based on genre or platform, I want that to be at least 95% guaranteed. Otherwise, if the scores are affected, we need to take those factors in account and make more games that have a better chance of impressing our users.

# ## Conclusion

# Action and sports games are the most popular genres of video games to play worldwide. No matter what platform these games are played on, their ratings by players are not affected. North America contributes the most sales to video games, followed by Europe, and relatively speaking, Japan does not contribute as much. Games that are sold on multiple platforms likely have a most popular platform the game is played on. The PS2 was the most popular platform for the the longest timeline for videogames.
