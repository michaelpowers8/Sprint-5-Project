# Video Game Data Analysis

# 
# <div class="alert alert-block alert-danger">
# <b>Overallv reviewer's comment</b> <a class="tocSkip"></a>
#     
# Path is still wrong.
# </div>

# The data from the ESRB will be analyzed in this notebook. After analysis is completed, it will be clearer which games succeeded and which did not. Also, it will help with advertising for the sales of video games next year.

# <div class="alert alert-block alert-warning">
# <b>Reviewer's comment</b> <a class="tocSkip"></a>
#     
# We should add more information about project here.
# </div>

# ## Preprocessing

# ### Initialization

# In[1]:


import pandas as pd
from matplotlib import pyplot as plt
from scipy import stats
import numpy as np
import random
import math
import seaborn as sns


# ### Load Data 

# In[2]:


df_games = pd.read_csv('/datasets/games.csv')


# ### Renaming Columns

# In[3]:


print(df_games.info())
print(df_games.head(5))


# In[4]:


print(df_games.columns)


# In[5]:


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


# ### Filling Empty Cells

# In[6]:


df_games['user_score'] = df_games['user_score'].replace(to_replace=['tbd',np.nan],value=-1)
df_games['critic_score'] = df_games['critic_score'].replace(to_replace=np.nan,value=-1)
df_games['year_of_release'] = df_games['year_of_release'].replace(to_replace=np.nan,value=-1)


# In[7]:


df_games['rating'] = df_games['rating'].fillna('Unknown')
df_games['genre'] = df_games['genre'].fillna('Unknown')


# ### Converting Data Types

# In[8]:


print(df_games['user_score'].unique())
print(df_games['critic_score'].unique())


# The year_of_release column will be changed to integers since years are not used with decimals. The user_score column should be floats, and scores with 'tbd' should be marked with empty scores for now to convert the column without an error. This ensures the remaining data will not appear skewed and confuse others when analyzing the data later. The critic_score will be changed to integers because all scores given by critics always end in .0 meaning no decimals were used originally.

# In[9]:


df_games['user_score'] = df_games['user_score'].astype('float64')


# In[10]:


df_games['year_of_release'] = df_games['year_of_release'].astype('int64')
df_games['critic_score'] = df_games['critic_score'].astype('int64')
df_games['user_score'] = df_games['user_score'].astype('float64')


# In[11]:


print(df_games['user_score'].sort_values().unique())
print(df_games['critic_score'].sort_values().unique())
print(df_games['year_of_release'].sort_values().unique())


# In[12]:


print(df_games.info())


# In[13]:


print(df_games.head(10))


# In[14]:


print(df_games[(df_games.duplicated())])


# No obvious duplicates. Now, it's time to search for implicit duplicates by printing duplicate names and seeing if they come from the same console.

# In[15]:


df_duplicate_games = df_games[df_games['name'].duplicated()]
df_duplicate_games = df_duplicate_games.groupby(['name','platform']).count().sort_values(by='genre',ascending=False)
print(df_duplicate_games.head(10))


# Three games have possible implicit duplicates: Need for Speed: Most Wanted, Madden NFL 13, and Sonic the Hedgehog. 
# These implicit duplicates need to be removed. All sales from the duplicate value will be added to the original to 
# ensure no lost sales counts in the data.

# In[16]:


print(df_games[df_games['name']=='Need for Speed: Most Wanted'])
print(df_games[df_games['name']=='Madden NFL 13'])
print(df_games[df_games['name']=='Sonic the Hedgehog'])


# Need for Speed actually does not have any duplicates to be removed. The game was released in 2005 and 2012
# on several different consoles. Madden NFL 13 and Sonic both have duplicate postings on the PS3. The year of 
# release in Sonic will be changed to 2006 since that's when its duplicate was released.

# In[17]:


df_games.loc[(df_games['name'] == 'Sonic the Hedgehog') & (df_games['year_of_release'] == -1),'year_of_release'] = 2006


# In[18]:


print(df_games[df_games['name']=='Madden NFL 13'])
print(df_games[df_games['name']=='Sonic the Hedgehog'])


# Now that all duplicates have been removed from the DataFrame, it is time to start enriching the data. 
# Start with finding the total sales of each game and creating a new column in the DataFrame for it.

# In[19]:


df_games['total_sales'] = df_games['na_sales'] + df_games['eu_sales'] + df_games['jp_sales'] + df_games['other_sales']
print(df_games.head(10))


# In[20]:


df_games[~(df_games['year_of_release']==-1)]['year_of_release'].plot(kind='hist',
            title='Yearly Released Games',
            xlabel='Year',
            ylabel='Number of Games',
            bins=len(df_games[~(df_games['year_of_release']==-1)]['year_of_release'].unique()))
plt.show()


# In[21]:


df_games[~(df_games['year_of_release']==-1)].groupby('year_of_release').count().plot(
            title='Yearly Released Games',
            xlabel='Year',
            ylabel='Number of Games',
            legend=False)
plt.show()


# The 1980s and early 1990s had very few video games released from year to year. 
# The number of games did not begin to increase until 2000. There is a large dropoff of games 
# released after 2011. Therefore the most significant timeline to analyze is 2000-2011.

# In[22]:


platform_sales = []
platform_choice = df_games['platform'].unique()
for platform in platform_choice:
    platform_sales.append([platform,round(df_games[(df_games['platform']==platform)]['total_sales'].sum(),2)])
print(platform_sales)


# In[23]:


df_games.groupby('platform')['total_sales'].sum().sort_values(ascending=False).plot(kind='bar',title='Total Platform Sales')
plt.show()


# The PS2 had the most total sales next to every other platform in this dataset. Now it is time 
# to build distributions on the PS2 data to see when they were popular, and use their primetime 
# years to evaluate how and why they were so successful.

# In[24]:


ps2_games = df_games[(df_games['platform']=='PS2')]
print(ps2_games.head())


# In[25]:


print(ps2_games.groupby('year_of_release')['name'].count())


# In[26]:


relevant_games = df_games


# In[27]:


print(relevant_games.groupby('platform')['total_sales'].sum().sort_values(ascending=False))


# In[28]:


relevant_games.groupby('platform')['total_sales'].sum().sort_values(ascending=False)[0:10].plot(
kind='pie',
autopct='%1.0f%%',
title='Total Platform Sales',
legend=False)


# In[29]:


top_10_platforms = ['PS2','X360','PS3','Wii','DS','PS','PS4','GBA','PSP','3DS']


# In this timeframe, besides the PS2, the DS, Wii, and XBOX 360 are leading in sales. 
# The PS3 is not too far behind. Let's see which of these are growing, and which are shrinking.

# In[30]:


for popular_platform in top_10_platforms:
    relevant_games[(relevant_games['platform']==popular_platform) & (relevant_games['year_of_release']!=-1)].groupby('year_of_release')['total_sales'].sum().plot()
plt.legend(top_10_platforms)
plt.show()


# In[31]:


figure,axis = plt.subplots(4,3)
x=0
y=0
for popular_platform in top_10_platforms:
    if(y==3):
        y=0
        x+=1
    axis[x,y].plot(relevant_games[(relevant_games['platform']==popular_platform) & (relevant_games['year_of_release']!=-1)].groupby('year_of_release')['total_sales'].sum())
    axis[x,y].set_title(f'{popular_platform} Sales')
    axis[x,y].set_xlim(1983,2018)
    axis[x,y].set_ylim(0,250)
    y+=1
plt.subplots_adjust(left=1,
                    bottom=1,
                    right=2,
                    top=3,
                    wspace=0.5,
                    hspace=0.5)
plt.show()


# If a platform is among the top 2-3 most popular, they have a popular phase of about 7 years, 
# and a relevance phase of 10 years. If a platform is average or below, it's popular for up to 
# 5 years, but has any relevance for up to 7 years.
# Throughout the whole timeline, the top 10 game consoles did not start gaining true popularity 
# until at least 1995. All data moving forward will be analyzed from 1995-2016 to make better predictions.

# In[32]:


relevant_games = df_games[(df_games['year_of_release'] > 1995) & (df_games['year_of_release'] <= 2016)]


# In[33]:


figure,axis = plt.subplots(6,int(relevant_games['platform'].nunique()/6))
x=0
y=0
for popular_platform in relevant_games['platform'].unique():
    if(y==int(relevant_games['platform'].nunique()/6)):
        y=0
        x+=1
    axis[x,y].plot(relevant_games[(relevant_games['platform']==popular_platform) & (relevant_games['year_of_release']!=-1)].groupby('year_of_release')['total_sales'].sum())
    axis[x,y].set_title(f'{popular_platform} Sales')
    axis[x,y].set_xlim(1995,2018)
    axis[x,y].set_ylim(0,250)
    y+=1
plt.subplots_adjust(left=1,
                    bottom=1,
                    right=3,
                    top=5,
                    wspace=0.5,
                    hspace=0.5)
plt.show()



# In[34]:


data = []
for platform in relevant_games['platform'].unique():
    data.append(relevant_games[relevant_games['platform']==platform].groupby('year_of_release')['total_sales'].sum())
plt.boxplot(data,vert=False,showfliers=True,labels=relevant_games['platform'].unique())
plt.show()


# In[35]:


data = []
for platform in top_10_platforms:
    data.append(relevant_games[relevant_games['platform']==platform].groupby('year_of_release')['total_sales'].sum())
plt.boxplot(data,vert=False,showfliers=True,labels=top_10_platforms)
plt.show()



# The difference in sales is very significant between platforms. The most popular 
# platforms have median yearly total sales over triple the less popular platforms. 
# For the largest platforms, their yearly sales were around 120, and the other 
# platforms had yearly sales around 40 or less. Given the timeframe covers the 
# entire existence of the ps2, it has the widest range of yearly sales. On the opposite 
# side, a platform like the 2600 only has data from one year, 2007, in this entire 
# timeframe. Therefore, its range is just one value. The most competitive platforms 
# in this timeframe to the PS2, besides the PS3 since they are the same company, was 
# the XBOX 360, DS, and Wii. 

# I will now take a closer look at the XBOX 360, my personal favorite console, 
# and see how its sales were affected by users, and professional critics. 

# In[36]:


xbox_games = relevant_games[relevant_games['platform']=='X360']


# In[37]:


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


# Based on the scatterplots, there seems to be a little correlation between sales 
# and scores of both critics and users. The effect is not noticed until the user 
# and critic scores are in the top about 20% of scores. The exception to this general 
# rule is the game that Nintendo geniusely included, Wii Sports. This strategy 
# provided all new players with an immediate game and a quick boost. Time to run 
# a quick formality of testing hypotheses on sales versus critics and users.

# Null Hypothesis: Total Sales are affected by the scores of critics, and users.

# Alternate Hypothesis: Total Sales are not affected by the scores of critics, and users.

# In[38]:


alpha = 0.05
results = stats.ttest_ind(xbox_games.groupby('year_of_release')['total_sales'].mean() , xbox_games.groupby('year_of_release')['user_score'].mean() , equal_var=True)

print('p-value:', results.pvalue)
if (results.pvalue < alpha):
    print("We reject the null hypothesis: sales were not significantly affected by user scores.")
else:
    print("We can't reject the null hypothesis: sales were significantly affected by user scores.")


# In[39]:


results = stats.ttest_ind(xbox_games.groupby('year_of_release')['total_sales'].mean() , xbox_games.groupby('year_of_release')['critic_score'].mean() , equal_var=True)

print('p-value:', results.pvalue)
if (results.pvalue < alpha):
    print("We reject the null hypothesis: sales were not significantly affected by critic scores.")
else:
    print("We can't reject the null hypothesis: sales were significantly affected by critic scores.")


# In[40]:


xbox_games.plot(
                kind='box',
                title='Sales vs Users',
                x='user_score',
                xlabel='User Score',
                ylabel='Total Sales (USD)',
                vert=False
)
xbox_games.plot(
                kind='box',
                title='Sales vs Critics',
                x='critic_score',
                xlabel='Critic Score',
                ylabel='Total Sales (USD)',
                vert=False
)


# ### Multiple Platforms

# In this section, I am now going to find the games that are in the relevant 
# timeframe of the data that are also on multiple platforms. 

# In[41]:


multiple_platforms = relevant_games.groupby('name')['platform'].nunique()


# In[42]:


multiple_platforms = relevant_games.groupby('name').agg(platforms=('platform', 'nunique'))
multiple_platform_game_names = multiple_platforms[multiple_platforms['platforms'] > 1].reset_index()['name']
relevant_multiplatform_games = relevant_games[relevant_games['name'].isin(multiple_platform_game_names)].copy()


# Now that we have the multiplatform games, it is time to compare how sales are for the games on each of their platforms separately. I am not certain on the best way to do this, so for now, I will just choose a random game from the dataframe and plot its sales per platform, and run several trials and make note of the results. 

# In[43]:


game = random.choice(relevant_multiplatform_games['name'].unique())
relevant_multiplatform_games[relevant_multiplatform_games['name']==game].sort_values(by='platform').plot(
    kind='scatter',
    x='platform',
    y='total_sales',
    title=f'{game} Sales by Platform',
    ylim=(0,relevant_multiplatform_games[relevant_multiplatform_games['name']==game]['total_sales'].sum())
)


# 

# Now it is time to compare sales by genre of games. To do this, I will make a 
# dataframe where each column name is a genre, and the entries will be the sale 
# totals for the games of those specific genres. Since putting in a bunch of zeros 
# for the empty cells will skew the averages greatly and make everything seem 
# less profitable, I will leave empty cells empty for now and just plot the 
# existing values on boxplots side by side.

# In[44]:


for genre in relevant_multiplatform_games['genre'].unique():
    relevant_multiplatform_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['total_sales']
sales_by_genre_df = pd.DataFrame(data=relevant_multiplatform_games[['Action', 'Shooter', 'Misc', 'Role-Playing', 'Simulation', 'Sports', 'Racing', 'Platform', 'Adventure', 'Fighting', 'Puzzle', 'Strategy']],columns=relevant_multiplatform_games['genre'].unique())
relevant_multiplatform_games = relevant_multiplatform_games.drop(columns=['Action', 'Shooter', 'Misc', 'Role-Playing', 'Simulation', 'Sports', 'Racing', 'Platform', 'Adventure', 'Fighting', 'Puzzle', 'Strategy'])

print(sales_by_genre_df)


# In[45]:


print(sales_by_genre_df.sum())


# In[46]:


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


# In[47]:


sales_by_genre_df.sum().sort_values(ascending=False).plot(
    kind='pie',
    title='Sales by Genre',
    autopct='%1.0f%%',
    subplots=True
)
plt.ylabel('')
plt.show()


# In[48]:


sales_by_genre_df.sum().sort_values(ascending=False).plot(
    kind='bar',
    title='Sales by Genre'
)
plt.ylabel('Total Sales (USD)')
plt.show()


# In[49]:


sales_by_genre_df.describe()


# Looking at all of the genres side by side, without outliers paints a better 
# general picture. Fighting games do better on average as the median sales is 
# largest and even its upper and lower quartiles are higher than the other genres. 
# However, when looking at the outliers, it can be argued that sports, action, and 
# shooter games are the most successful. However, for these genres, if the games 
# are not exceptional, they will not do as well.

# ## Regional Sales

# It is now time to determine the 5 most popular platforms and genres of each region 
# and figure out if the ESRB rating affects the sales in each region. Starting with North America.

# ### North America Platforms

# In[50]:


na_relevant_games = relevant_games[relevant_games['na_sales']>0]


# In[51]:


platform_sales.clear()
for platform in platform_choice:
    platform_sales.append([platform,round(na_relevant_games[(na_relevant_games['platform']==platform)]['na_sales'].sum(),2)])
print(platform_sales)


# Based on the sales list of each platform in North America, the top 5 most popular platforms are 
# 1. PS2 
# 2. Wii
# 3. XBOX 360 
# 4. DS
# 5. PS3 
# I will now also count how many games were sold on each platform. This will 
# ensure that the sales of very popular games do not leave the less popular 
# games out of the picture.

# In[52]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    count = na_relevant_games[na_relevant_games['platform']==platform]['platform'].count()
    print(f'{platform}: {count}')


# Based on just number of games sold on each of the 5 platforms, the popularity ranking is:
# 1. PS2
# 2. DS
# 3. Wii
# 4. XBOX 360
# 5. PS3 
# To make a final conclusion, I will make boxplot and piechart distributions of each of the sales of the platforms.

# In[53]:


print(na_relevant_games.groupby(['platform']).sum().sort_values(by='na_sales',ascending=False)[0:5])


# In[54]:


na_relevant_games.groupby(['platform']).sum().sort_values(by='na_sales',ascending=False)[0:5].plot(kind='pie',
                                                    title='North American Platforms',
                                                    y='na_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[55]:


data = (na_relevant_games.pivot_table(index='platform', values='na_sales', aggfunc='sum').sort_values('na_sales', ascending=False).head()).reset_index()
sns.set_color_codes("pastel")
sns.barplot(y=data['platform'], x=data['na_sales'], data=data, label="sales")
sns.set_color_codes("muted")
plt.show()


# In[56]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    na_relevant_games[platform] = relevant_multiplatform_games[relevant_multiplatform_games['platform']==platform]['na_sales']
na_sales_by_platform_df = pd.DataFrame(data=na_relevant_games[['PS2','Wii','X360','DS','PS3']],columns=['PS2','Wii','X360','DS','PS3'])
na_relevant_games = na_relevant_games.drop(columns=['PS2','Wii','X360','DS','PS3'])


# In[57]:


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


# In conclusion based on the box plots and the pie chart, the 5 most popular platforms in North America are:
# 1. PS2
# 2. Wii
# 3. Xbox 360
# 4. DS
# 5. PS3

# ### Europe Platforms

# In[58]:


eu_relevant_games = relevant_games[relevant_games['eu_sales']>0]


# In[59]:


platform_sales.clear()
for platform in platform_choice:
    platform_sales.append([platform,round(na_relevant_games[(na_relevant_games['platform']==platform)]['eu_sales'].sum(),2)])
print(platform_sales)


# Based on the sales list of each platform in Europe, the top 5 most popular platforms are 
# 1. PS2 
# 2. Wii
# 3. PS3 
# 4. XBOX 360
# 5. DS
# I will now also count how many games were sold on each platform. This will 
# ensure that the sales of very popular games do not leave the less popular games out of the picture.

# In[60]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    count = eu_relevant_games[eu_relevant_games['platform']==platform]['platform'].count()
    print(f'{platform}: {count}')


# Based on just number of games sold on each of the 5 platforms, the popularity ranking is:
# 1. PS2
# 2. DS
# 3. XBOX 360
# 4. Wii
# 5. PS3
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[61]:


eu_relevant_games.groupby(['platform']).sum().sort_values(by='eu_sales',ascending=False)[0:5].plot(kind='pie',
                                                    title='European Sales',
                                                    y='eu_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[62]:


data = (na_relevant_games.pivot_table(index='platform', values='eu_sales', aggfunc='sum').sort_values('eu_sales', ascending=False).head()).reset_index()
sns.set_color_codes("pastel")
sns.barplot(y=data['platform'], x=data['eu_sales'], data=data, label="sales")
sns.set_color_codes("muted")
plt.show()


# In[63]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    eu_relevant_games[platform] = relevant_multiplatform_games[relevant_multiplatform_games['platform']==platform]['eu_sales']
eu_sales_by_platform_df = pd.DataFrame(data=eu_relevant_games[['PS2','Wii','X360','DS','PS3']],columns=['PS2','Wii','X360','DS','PS3'])
eu_relevant_games = eu_relevant_games.drop(columns=['PS2','Wii','X360','DS','PS3'])


# In[64]:


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


# Based on the sales list of each platform in Europe, the top 5 most popular platforms are 
# 1. PS2 
# 2. Wii
# 3. PS3 
# 4. XBOX 360
# 5. DS

# ### Japan Platforms

# In[65]:


jp_relevant_games = relevant_games[relevant_games['jp_sales']>0]


# In[66]:


platform_sales.clear()
for platform in platform_choice:
    platform_sales.append([platform,round(jp_relevant_games[(jp_relevant_games['platform']==platform)]['jp_sales'].sum(),2)])
print(platform_sales)


# Based on the sales list of each platform in Europe, the top 5 most popular platforms are 
# 1. DS 
# 2. PS2
# 3. PSP 
# 4. Wii
# 5. PS3
# I will now also count how many games were sold on each platform. This 
# will ensure that the sales of very popular games do not leave the less 
# popular games out of the picture.

# In[67]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    count = jp_relevant_games[jp_relevant_games['platform']==platform]['platform'].count()
    print(f'{platform}: {count}')


# Based on just number of games sold on each of the 5 platforms, the popularity ranking is:
# 1. PS2
# 2. DS
# 3. PS3
# 4. XBOX 360
# 5. Wii
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[68]:


jp_relevant_games.groupby(['platform']).sum().sort_values(by='jp_sales',ascending=False)[0:5].plot(kind='pie',
                                                    title='Japanese Sales',
                                                    y='jp_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[69]:


data = (jp_relevant_games.pivot_table(index='platform', values='jp_sales', aggfunc='sum').sort_values('jp_sales', ascending=False).head()).reset_index()
sns.set_color_codes("pastel")
sns.barplot(y=data['platform'], x=data['jp_sales'], data=data, label="sales")
sns.set_color_codes("muted")
plt.show()


# In[70]:


for platform in ['PS2','Wii','X360','DS','PS3']:
    jp_relevant_games[platform] = relevant_multiplatform_games[relevant_multiplatform_games['platform']==platform]['jp_sales']
jp_sales_by_platform_df = pd.DataFrame(data=jp_relevant_games[['PS2','Wii','X360','DS','PS3']],columns=['PS2','Wii','X360','DS','PS3'])
jp_relevant_games = jp_relevant_games.drop(columns=['PS2','Wii','X360','DS','PS3'])


# In[71]:


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
# based on the boxplot and the pie chart, the top 5 most popular platforms are:
# 1. DS
# 2. PS2
# 3. PSP
# 4. Wii
# 5. GBA

# ### North America Genres

# In[72]:


na_relevant_games_genres_sales = []
for genre in na_relevant_games['genre'].unique():
    na_relevant_games_genres_sales.append([genre,round(na_relevant_games[(na_relevant_games['genre']==genre)]['na_sales'].sum(),2)])
print(na_relevant_games_genres_sales)


# Based on the sales list of each genre in North America, the top 5 most popular genres are 
# 1. Action 
# 2. Sports
# 3. Shooter 
# 4. Miscellaneous
# 5. Racing
# I will now also count how many games were sold in each genre. This will 
# ensure that the sales of very popular games do not leave the less 
# popular games out of the picture.

# In[73]:


na_relevant_games_genres_num_games = []
for genre in ['Action','Sports','Shooter','Misc','Racing']:
    na_relevant_games_genres_num_games.append([genre,na_relevant_games[(na_relevant_games['genre']==genre)]['na_sales'].count()])
print(na_relevant_games_genres_num_games)


# Based on just number of games sold in each of the 5 genres, the popularity ranking is:
# 1. Action
# 2. Sports
# 3. Miscellaneous
# 4. Racing
# 5. Shooter
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[74]:


na_relevant_games.groupby(['genre']).sum().sort_values(by='na_sales',ascending=False)[0:5].plot(kind='pie',
                                                    title='North American Genres',
                                                    y='na_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[75]:


for genre in ['Action','Sports','Shooter','Misc','Racing']:
    na_relevant_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['na_sales']
na_sales_by_genre_df = pd.DataFrame(data=na_relevant_games[['Action','Sports','Shooter','Misc','Racing']],columns=['Action','Sports','Shooter','Misc','Racing'])
na_relevant_games = na_relevant_games.drop(columns=['Action','Sports','Shooter','Misc','Racing'])


# In[76]:


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

# In[77]:


eu_relevant_games_genres_sales = []
for genre in eu_relevant_games['genre'].unique():
    eu_relevant_games_genres_sales.append([genre,round(na_relevant_games[(na_relevant_games['genre']==genre)]['eu_sales'].sum(),2)])
print(eu_relevant_games_genres_sales)


# Based on the sales list of each genre in Europe, the top 5 most popular genres are 
# 1. Action 
# 2. Sports
# 3. Shooter 
# 4. Racing
# 5. Miscellaneous
# I will now also count how many games were sold in each genre. This 
# will ensure that the sales of very popular games do not leave the 
# less popular games out of the picture.

# In[78]:


eu_relevant_games_genres_num_games = []
for genre in ['Action','Sports','Shooter','Misc','Racing']:
    eu_relevant_games_genres_num_games.append([genre,eu_relevant_games[(eu_relevant_games['genre']==genre)]['eu_sales'].count()])
print(eu_relevant_games_genres_num_games)


# Based on just number of games sold in each of the 5 genres, the popularity ranking is:
# 1. Action
# 2. Sports
# 3. Miscellaneous
# 4. Racing
# 5. Shooter
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[79]:


eu_relevant_games.groupby(['genre']).sum().sort_values(by='eu_sales',ascending=False)[0:5].plot(kind='pie',
                                                    title='European Genres',
                                                    y='eu_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[80]:


for genre in ['Action','Sports','Shooter','Misc','Racing']:
    eu_relevant_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['eu_sales']
eu_sales_by_genre_df = pd.DataFrame(data=eu_relevant_games[['Action','Sports','Shooter','Misc','Racing']],columns=['Action','Sports','Shooter','Misc','Racing'])
eu_relevant_games = eu_relevant_games.drop(columns=['Action','Sports','Shooter','Misc','Racing'])


# In[81]:


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

# In[82]:


jp_relevant_games_genres_sales = []
for genre in jp_relevant_games['genre'].unique():
    jp_relevant_games_genres_sales.append([genre,round(jp_relevant_games[(jp_relevant_games['genre']==genre)]['jp_sales'].sum(),2)])
print(jp_relevant_games_genres_sales)


# Based on the sales list of each genre in Europe, the top 5 most popular genres are 
# 1. Role-Playing 
# 2. Action
# 3. Miscellaneous 
# 4. Sports
# 5. Platform
# I will now also count how many games were sold in each genre. This 
# will ensure that the sales of very popular games do not leave the 
# less popular games out of the picture.

# In[83]:


jp_relevant_games_genres_num_games = []
for genre in ['Role-Playing','Action','Misc','Sports','Platform']:
    jp_relevant_games_genres_num_games.append([genre,jp_relevant_games[(jp_relevant_games['genre']==genre)]['jp_sales'].count()])
print(jp_relevant_games_genres_num_games)


# Based on just number of games sold in each of the 5 genres, the popularity ranking is:
# 1. Role-Playing
# 2. Action
# 3. Sports
# 4. Miscellaneous
# 5. Platform
# To make a final conclusion, I will make boxplot distributions of each of the sales of the platforms.

# In[84]:


jp_relevant_games.groupby(['genre']).sum().sort_values(by='jp_sales',ascending=False)[0:5].plot(kind='pie',
                                                    title='Japanese Genres',
                                                    y='jp_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[85]:


for genre in ['Role-Playing','Action','Misc','Sports','Platform']:
    jp_relevant_games[genre] = relevant_multiplatform_games[relevant_multiplatform_games['genre']==genre]['jp_sales']
jp_sales_by_genre_df = pd.DataFrame(data=jp_relevant_games[['Role-Playing','Action','Misc','Sports','Platform']],columns=['Role-Playing','Action','Misc','Sports','Platform'])
jp_relevant_games = jp_relevant_games.drop(columns=['Role-Playing','Action','Misc','Sports','Platform'])


# In[86]:


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

# In[87]:


na_relevant_games_rating_sales = []
for rating in na_relevant_games['rating'].unique():
    na_relevant_games_rating_sales.append([rating,round(na_relevant_games[(na_relevant_games['rating']==rating)]['na_sales'].sum(),2)])
print(na_relevant_games_rating_sales)


# Based on rating sales alone, it seems like games rated E are the 
# most popular. Hoowever, it's likely that more games are made rated E. 
# Let's make some boxplots to see the distribution of sales of games based on rating.

# In[88]:


na_relevant_games.groupby(['rating']).sum().sort_values(by='na_sales',ascending=False).plot(kind='pie',
                                                    title='North American Ratings',
                                                    y='na_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[89]:


for rating in ['E','Unknown','M','T','E10+','AO','EC']:
    na_relevant_games[rating] = relevant_multiplatform_games[relevant_multiplatform_games['rating']==rating]['na_sales']
na_sales_by_genre_df = pd.DataFrame(data=na_relevant_games[['E','Unknown','M','T','E10+','AO','EC']],columns=['E','Unknown','M','T','E10+','AO','EC'])
na_relevant_games = na_relevant_games.drop(columns=['E','Unknown','M','T','E10+','AO','EC'])


# In[90]:


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

# In[91]:


eu_relevant_games_rating_sales = []
for rating in eu_relevant_games['rating'].unique():
    eu_relevant_games_rating_sales.append([rating,round(eu_relevant_games[(eu_relevant_games['rating']==rating)]['eu_sales'].sum(),2)])
print(eu_relevant_games_rating_sales)


# In[92]:


eu_relevant_games.groupby(['rating']).sum().sort_values(by='eu_sales',ascending=False).plot(kind='pie',
                                                    title='European Ratings',
                                                    y='eu_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[93]:


for rating in ['E','Unknown','M','T','E10+','AO','EC']:
    eu_relevant_games[rating] = relevant_multiplatform_games[relevant_multiplatform_games['rating']==rating]['eu_sales']
eu_sales_by_genre_df = pd.DataFrame(data=eu_relevant_games[['E','Unknown','M','T','E10+','AO','EC']],columns=['E','Unknown','M','T','E10+','AO','EC'])
eu_relevant_games = eu_relevant_games.drop(columns=['E','Unknown','M','T','E10+','AO','EC'])


# In[94]:


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

# In[95]:


jp_relevant_games_rating_sales = []
for rating in na_relevant_games['rating'].unique():
    jp_relevant_games_rating_sales.append([rating,round(jp_relevant_games[(jp_relevant_games['rating']==rating)]['eu_sales'].sum(),2)])
print(jp_relevant_games_rating_sales)


# In[96]:


jp_relevant_games.groupby(['rating']).sum().sort_values(by='jp_sales',ascending=False).plot(kind='pie',
                                                    title='Japan Ratings',
                                                    y='jp_sales',
                                                    autopct='%1.0f%%'
                                                   )
plt.legend([])
plt.show()


# In[97]:


for rating in ['E','Unknown','M','T','E10+','AO','EC']:
    jp_relevant_games[rating] = relevant_multiplatform_games[relevant_multiplatform_games['rating']==rating]['jp_sales']
jp_sales_by_genre_df = pd.DataFrame(data=jp_relevant_games[['E','Unknown','M','T','E10+','AO','EC']],columns=['E','Unknown','M','T','E10+','AO','EC'])
jp_relevant_games = jp_relevant_games.drop(columns=['E','Unknown','M','T','E10+','AO','EC'])


# In[98]:


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


# ### Summary
# * In the USA:
# * The xbox 360 is the most popular, second one is PS2. The others in the 
# top 5 are not at the same level. The ongoing argument in America is xbox or playstation. 

# * The top 3 genres are:
# 1. Action
# 2. Sports
# 3. Shooter
# * All other genres are way below these 3.
# * The top ratings are E, T, and M. With so many unknowns, this is not the best way to determine if rating affects sales.
# 
# * In Europe:
# * The playstation consoles are the most popular in Europe. The xbox does compete but not nearly as much as playstation.
# * The top 3 genres are:
# 1. Action
# 2. Sports
# 3. Shooter
# * All other genres are way below these 3.
# * The top ratings are E, T, and M. With so many unknowns, this is not the best way to determine if rating affects sales.
# 
# * In Japan:
# * The DS, PS2, and PS are the most popular. Japan has a lot higher ercentage of hand-held gaming.
# * The top 3 genres are:
# 1. Role-playing
# 2. Action
# 3. Sports
# * All other genres are way below these 3. Role-playing is by far the absolute most popular
# * The top ratings are E and T but this is unreliable with over half the sales made are with unknown ratings.

# ## Test Hypotheses

# ### XBOX vs PC

# Null Hypothesis: 
# The user score is not affected if a game is played on the XBOX One or the PC.

# Alternate Hypothesis: 
# The user score is affected if a game is played on the XBOX One or the PC.

# In[99]:


alpha = 0.05
xbox = relevant_games[(relevant_games['platform'].isin(['XB','XOne','X360'])) & (relevant_games['user_score']!=-1)]['user_score'].values
pc = relevant_games[(relevant_games['platform']=='PC') & (relevant_games['user_score']!=-1)]['user_score'].values
results = stats.ttest_ind(xbox, pc)

print(f'p-value: {results.pvalue}')
if (results.pvalue < alpha):
    print("We reject the null hypothesis: user score was affected by the platform chosen.")
else:
    print("We can't reject the null hypothesis: user score was not significantly affected based on the platform.")


# ### Action vs Sports

# Null Hypothesis: The user score is not affected depending on if a game is labeled 'Action' or 'Sports.'

# Alternate Hypothesis: The user score is affected depending on if a game is labeled 'Action' or 'Sports.'

# In[100]:


alpha = 0.05
action = relevant_games[(relevant_games['genre']=='Action') & (relevant_games['user_score']!=-1)]['user_score'].values
sports = relevant_games[(relevant_games['genre']=='Sports') & (relevant_games['user_score']!=-1)]['user_score'].values
results = stats.ttest_ind(action , sports)

print(f'p-value: {results.pvalue}')
if (results.pvalue < alpha):
    print("We reject the null hypothesis: user score was affected by genre.")
else:
    print("We can't reject the null hypothesis: user score was not significantly affected by the genre.")


# I formulated the null hypothesis by asking myself "Does platform affect the user score?" 
# and "Does genre affect the user score?" Then, I rephrased that question and assumed and 
# rewrote statements that assume there is no relationship between genres, platforms, and user scores.

# The significance level I chose for these tests were 0.05 because if I am telling 
# the company that user ratings are not affected based on genre or platform, I want 
# that to be at least 95% guaranteed. Otherwise, if the scores are affected, we need 
# to take those factors in account and make more games that have a better chance of 
# impressing our users.

# ## Conclusion

# Action and sports games are the most popular genres of video games to play worldwide. 
# No matter what platform these games are played on, their ratings by players are 
# not affected. North America contributes the most sales to video games, followed by 
# Europe, and relatively speaking, Japan does not contribute as much. Games that are 
# sold on multiple platforms likely have a most popular platform the game is played on. 
# The PS2 was the most popular platform for the the longest timeline for videogames. 
# Only the best of the best platforms have a popularity lifetime of maybe 10 years. 
# Otherwise, most consoles are relevant about 6 years. It is unreliable, especially in 
# Japan, to forecast sales for new games by ESRB. However, platform and genre do matter a little more. 