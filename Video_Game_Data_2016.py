# %% [markdown]
# #Video Game Data Analysis

# %% [markdown]
# The data from the ESRB will be analyzed in this notebook. After analysis is completed, it will be clearer which games succeeded and which did not. Also, it will help with advertising for the sales of video games next year.

# %%
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from scipy import stats
import numpy as np

# %%
df_games = pd.read_csv('moved_games.csv')
print(df_games.info())

# %%
print(df_games.head(5))

# %%
print(df_games.columns)

# %%
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
print(df_games.columns)

# %%
print(df_games['user_score'].unique())
print(df_games['critic_score'].unique())

# %% [markdown]
# This cell will first fill empty cells with appropriate default values. Then, the year_of_release column will be changed to integers since years are not used with decimals. The user_score column should be floats, and scores with 'tbd' should be marked with the median score. This ensures the remaining data will not appear skewed and confuse others when analyzing the data later. The critic_score will be changed to integers because all scores given by critics always end in .0 meaning no decimals were used originally.

# %%
df_games['year_of_release'] = df_games['year_of_release'].fillna(df_games['year_of_release'].median())
df_games['rating'] = df_games['rating'].fillna('Unknown')
df_games['critic_score'] = df_games['critic_score'].fillna(df_games['critic_score'].median())
df_games['genre'] = df_games['genre'].fillna('Unknown')

# %%
df_games['user_score'] = df_games['user_score'].replace(to_replace='tbd',value=None)
df_games['user_score'] = df_games['user_score'].fillna(df_games['user_score'].median())
df_games['user_score'] = df_games['user_score'].astype('float64')

# %%
df_games['year_of_release'] = df_games['year_of_release'].astype('int64')
df_games['critic_score'] = df_games['critic_score'].astype('int64')
df_games['user_score'] = df_games['user_score'].astype('float64')

# %%
print(df_games['user_score'].sort_values().unique())
print(df_games['critic_score'].sort_values().unique())
print(df_games['year_of_release'].sort_values().unique())

# %%
print(df_games.info())

# %%
print(df_games.head(10))

# %% [markdown]
# Now that the empty cells have been filled, it is time to search for duplicate games. I will search for obvious duplicates first, and then implicit duplicates after. The duplicates will all be from the name of the games being played on the same console.

# %%
print(df_games[(df_games.duplicated())])

# %% [markdown]
# No obvious duplicates. Now, it's time to search for implicit duplicates by printing duplicate names and seeing if they come from the same console.

# %%
df_duplicate_games = df_games[df_games['name'].duplicated()]
df_duplicate_games = df_duplicate_games.groupby(['name','platform']).count().sort_values(by='genre',ascending=False)
print(df_duplicate_games.head(10))

# %% [markdown]
# Three games have possible implicit duplicates: Need for Speed: Most Wanted, Madden NFL 13, and Sonic the Hedgehog. These implicit duplicates need to be removed. All sales from the duplicate value will be added to the original to ensure no lost sales counts in the data.

# %%
print(df_games[df_games['name']=='Need for Speed: Most Wanted'])
print(df_games[df_games['name']=='Madden NFL 13'])
print(df_games[df_games['name']=='Sonic the Hedgehog'])

# %% [markdown]
# Need for Speed actually does not have any duplicates to be removed. The game was released in 2005 and 2012 on several different consoles. Madden and Sonic both have duplicate postings on the PS3. The dupicates will now be removed and the sales from the duplicate post will be added to the original.

# %%
df_games.loc[(df_games['name'] == 'Madden NFL 13') & (df_games['eu_sales'] == 0.22),'eu_sales'] = 0.23
df_games.loc[(df_games['name'] == 'Sonic the Hedgehog') & (df_games['eu_sales'] == 0.06),'eu_sales'] = 0.54
df_games.drop(4127,inplace=True)
df_games.drop(16230,inplace=True)


# %%
print(df_games[df_games['name']=='Madden NFL 13'])
print(df_games[df_games['name']=='Sonic the Hedgehog'])

# %% [markdown]
# Now that all duplicates have been removed from the DataFrame, it is time to start enriching the data. Start with finding the total sales of each game and creating a new column in the DataFrame for it.

# %%
df_games['total_sales'] = df_games['na_sales'] + df_games['eu_sales'] + df_games['jp_sales'] + df_games['other_sales']
print(df_games.head(10))

# %%
platform_sales = []
platform_choice = df_games['platform'].unique()
for platform in platform_choice:
    platform_sales.append([platform,round(df_games[(df_games['platform']==platform)]['total_sales'].sum(),2)])
print(platform_sales)

# %% [markdown]
# The PS2 had the most total sales next to every other platform in this dataset. Now it is time to build distributions on the PS2 data to see when they were popular, and use their primetime years to evaluate how and why they were so successful.

# %%
ps2_games = df_games[(df_games['platform']=='PS2')]
print(ps2_games.head())

# %%
print(ps2_games.groupby('year_of_release')['name'].count())

# %% [markdown]
# Based on the ps2 data by year, the platform was creating games from 2000-2011. This is the time period I will be focusing on to further analyze the data.

# %%
relevant_games = df_games[(df_games['year_of_release'] >= 2000) & (df_games['year_of_release'] <= 2011)]

# %%
print(relevant_games.groupby('platform')['total_sales'].sum())

# %% [markdown]
# In this timeframe, besides the PS2, the DS, Wii, and XBOX 360 are leading in sales. The PS3 is not too far behind. Let's see which of these are growing, and which are shrinking.

# %%
for popular_platform in ['PS2','X360','PS3','Wii','DS','GBA']:
    relevant_games[relevant_games['platform']==popular_platform].groupby('year_of_release')['total_sales'].sum().plot()
plt.legend(['PS2','X360','PS3','Wii','DS','GBA'])
plt.show()

# %% [markdown]
# In this timeframe, we saw the ps2 rise and fall, along with the DS, and even the Wii. The XBOX 360 was still high and it is inconclusive if it was falling, or if it just had a slow year. With the fall of the PS2, it was clear that the rise of the PS3 was underway. A very successful platform maybe has a lifespan of popularity of about 10 years. An average platform seems to rise and fall in about 6-7 years.

# %%
data = []
for platform in relevant_games['platform'].unique():
    data.append(relevant_games[relevant_games['platform']==platform].groupby('year_of_release')['total_sales'].sum())
plt.boxplot(data,vert=False,showfliers=True,labels=relevant_games['platform'].unique())
plt.show()

# %% [markdown]
# The difference in sales is very significant between platforms. The most popular platforms have median yearly total sales over triple the less popular platforms. For the largest platforms, their yearly sales were around 120, and the other platforms had yearly sales around 40 or less. Given the timeframe covers the entire existence of the ps2, it has the widest range of yearly sales. On the opposite side, a platform like the 2600 only has data from one year, 2007, in this entire timeframe. Therefore, its range is just one value. The most competitive platforms in this timeframe to the PS2, besides the PS3 since they are the same company, was the XBOX 360, DS, and Wii. 

# %% [markdown]
# I will now take a closer look at the XBOX 360, my personal favorite console, and see how its sales were affected by users, and professional critics. 

# %%
xbox_games = relevant_games[relevant_games['platform']=='X360']

# %%
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

# %% [markdown]
# Based on the scatterplots, there seems to be a little correlation between sales and scores of both critics and users. The effect is not noticed until the user and critic scores are in the top about 20% of scores. The exception to this general rule is the game that Nintendo geniusely included, Wii Sports. This strategy provided all new players with an immediate game and a quick boost. Time to run a quick formality of testing hypotheses on sales versus critics and users.

# %% [markdown]
# Null Hypothesis: Total Sales are affected by the scores of critics, and users.

# %% [markdown]
# Alternate Hypothesis: Total Sales are not affected by the scores of critics, and users.

# %%
alpha = 0.05
results = stats.ttest_ind(xbox_games.groupby('year_of_release')['total_sales'].mean() , xbox_games.groupby('year_of_release')['user_score'].mean() , equal_var=True)

print('p-value:', results.pvalue)
if (results.pvalue < alpha):
    print("We reject the null hypothesis: sales were not significantly affected by user scores.")
else:
    print("We can't reject the null hypothesis: sales were significantly affected by user scores.")

# %%
results = stats.ttest_ind(xbox_games.groupby('year_of_release')['total_sales'].mean() , xbox_games.groupby('year_of_release')['critic_score'].mean() , equal_var=True)

print('p-value:', results.pvalue)
if (results.pvalue < alpha):
    print("We reject the null hypothesis: sales were not significantly affected by critic scores.")
else:
    print("We can't reject the null hypothesis: sales were significantly affected by critic scores.")

# %%
print(relevant_games.count())

# %%
multiple_platforms = relevant_games.groupby('name').count()
multiple_platforms = multiple_platforms[multiple_platforms['platform']>1]
print(multiple_platforms.sample(5))

# %% [markdown]
# it's time to start building the streamlit app. I will give the app a table sorted by console since companies and players compare their games by the consoles played on. Then, I will also build scatterplots that will help show correlation between scores by critics or users, and resulting sales. If there is a correlation anywhere, this will help the companies determine who should be impressed, and how to better advertise their upcoming games.

# %%
st.header('Video Game Sales')
st.write('''
         Filter the data by platform to see the data of many video games and their popularity and sales.
         ''')

# %%
make_choice_platform = st.selectbox('Select Platform:',platform_choice)

# %%
min_year,max_year = (df_games['year_of_release'].min() , df_games['year_of_release'].max())
year_range = st.slider(label='Choose year',step=int(1),min_value=int(min_year),max_value=int(max_year),value=(int(min_year),int(max_year)))

# %%
actual_range = list(range(year_range[0],year_range[1]+1))

# %%
filtered_type = df_games[(df_games['platform']==make_choice_platform) & (df_games['year_of_release'].isin(list(actual_range)))]
st.table(filtered_type.head(10))

# %%
st.header('Game Success Analysis')
st.write("""
Let's see what influences the success of a game the most. We will compare total sales to user_score, critic_score, genre and rating.""")

# %%
import plotly.express as px

list_for_scatter = ['genre','critic_score','user_score','rating']
choice_for_scatter = st.selectbox('Game sales dependency on ',list_for_scatter)
scatter = px.scatter(df_games , x='total_sales' , y=choice_for_scatter , hover_data=['year_of_release'])
scatter.update_layout(title="<b> Price vs {}<b>".format(choice_for_scatter))
st.plotly_chart(scatter)

# %%
list_for_scatter_2 = ['genre','critic_score','total_sales','rating']
choice_for_scatter_2 = st.selectbox('Game user popularity dependency on ',list_for_scatter_2)
scatter_2 = px.scatter(df_games , x='user_score' , y=choice_for_scatter_2 , hover_data=['year_of_release'])
scatter_2.update_layout(title="<b> Price vs {}<b>".format(choice_for_scatter_2))
st.plotly_chart(scatter_2)

# %%
list_for_scatter_3 = ['genre','user_score','total_sales','rating']
choice_for_scatter_3 = st.selectbox('Game critic popularity dependency on ',list_for_scatter_3)
scatter_3 = px.scatter(df_games , x='critic_score' , y=choice_for_scatter_3 , hover_data=['year_of_release'])
scatter_3.update_layout(title="<b> Price vs {}<b>".format(choice_for_scatter_3))
st.plotly_chart(scatter_3)


