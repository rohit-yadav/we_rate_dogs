
# coding: utf-8

# 
# # We Rate Dogs
# 
# WeRateDogs is a Twitter account that rates people's dogs with a humorous comment about the dog. These ratings almost always have a denominator of 10. The numerators, though? Almost always greater than 10. 11/10, 12/10, 13/10, etc. Why? Because "they're good dogs Brent." WeRateDogs has over 4 million followers and has received international media coverage.
# I will do a wrangling, analyzing and visualization of the tweet data of the WeRateDogs.

# In[1]:


# Import modules
import json
import os
import time
import pandas as pd
import numpy as np
import requests
import tweepy
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud,STOPWORDS


# In[2]:


# Twitter api
consumer_key = 'HIDDEN'
consumer_secret = 'HIDDEN'
access_token = 'HIDDEN'
access_secret = 'HIDDEN'

# Function to get twitter connection
def twitter_connection(consumer_key, consumer_secret, access_token, access_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    return api


# In[3]:


api = twitter_connection(consumer_key, consumer_secret, access_token, access_secret)


# In[4]:


# Downloading data from the url
url = 'https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'

# Request the url
r = requests.get(url)


# In[5]:


# Store the downloaded data
folder_name = 'data'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

with open('data/image_predictions.tsv', 'wb') as file:
    file.write(r.content)


# In[6]:


# Read the data into a data frame
archive_df = pd.read_csv("data/twitter-archive-enhanced.csv")
predictions_df = pd.read_csv("data/image_predictions.tsv", sep="\t")


# In[7]:


# Getting tweet ids
archive_tweet_id = list(archive_df.tweet_id)
prediction_tweet_id = list(predictions_df.tweet_id)


# In[8]:


len(archive_tweet_id)


# In[9]:


len(prediction_tweet_id)


# In[10]:


tweet_ids = archive_tweet_id + prediction_tweet_id


# In[11]:


len(tweet_ids)


# In[12]:


# Keeping unique tweet ids
tweet_ids = list(set(tweet_ids))


# In[13]:


len(tweet_ids)


# In[14]:


# Extracting tweet details from the API and storing it in a .txt file
# Collecting id which are still there
working_ids = []

# Tweet id of tweet which are deleted
removed_ids = []

def get_tweet_details():
    if os.path.isfile("data/tweet_json.txt"):
        print("File exists, no need to extract again")
        value = 0
    else:
        # Count the progress
        count = 0

        # Opening a file to write on
        with open('data/tweet_json.txt', 'w') as file:
            start = time.time()
            for tweet_id in tweet_ids:
                count = count + 1
                # Writing the data to a file - line by line
                try:
                    status = api.get_status(tweet_id, tweet_mode = 'extended')
                    file.write(json.dumps(status._json))
                    file.write('\n')
                    working_ids.append(tweet_id)
                    print("{}) Successful id: {}".format(count, tweet_id))
                # Handeling exception
                except:
                    removed_ids.append(tweet_id)
                    print("{}) Failed id: {}".format(count, tweet_id))
            end = time.time()
            print("Time taken: {}".format(end - start))
        value = 1
    return value


# In[15]:


value = get_tweet_details()


# In[16]:


if value == 1:
    print(len(working_ids))
    print(len(removed_ids))
else:
    print("File is alread present so this is not needed")


# In[17]:


# To hold the tweets details
all_tweets = []

# Read the file to add the details to a list
with open("data/tweet_json.txt") as f:
    for line in f:
        # Converting the string into a dictionary
        data = json.loads(line) 
        all_tweets.append(data)

# Creating a data frame with all the tweet details
all_tweet_df = pd.DataFrame(all_tweets)


# **Now we have three data frames**
# - all_tweet_df - Extracted from the API
# - archive_df - Got from Udacity
# - predictions_df- Downloaded from the url

# In[18]:


# Making a copy of the data frames
archive_clean = archive_df.copy()
all_tweet_clean = all_tweet_df.copy()
predictions_clean = predictions_df.copy()


# In[19]:


archive_clean.head()


# In[20]:


all_tweet_clean.head()


# In[21]:


predictions_clean.head()


# In[22]:


archive_df.info()


# In[23]:


all_tweet_clean.info()


# In[24]:


predictions_clean.info()


# In[25]:


archive_clean.describe()


# In[26]:


all_tweet_clean.describe()


# In[27]:


predictions_clean.describe()


# In[28]:


archive_clean[archive_clean.retweeted_status_id.notnull()].head()


# In[29]:


archive_clean[archive_clean.rating_denominator != 10].head()


# In[30]:


archive_clean[archive_clean.rating_numerator < 10].head()


# In[32]:


archive_clean[archive_clean.name == "a"].head()


# In[33]:


archive_clean.source.value_counts()


# In[34]:


archive_clean.rating_numerator.value_counts()


# In[35]:


archive_clean.rating_denominator.value_counts()


# ### Quality 
# 
# `archive_clean` table
# 
# - Timestamp should be converted to datatime
# - Retweeted tweets which are 181 of all the tweets
# - In in_reply_tweets doesn't have ratings in all of them
# - The html tags doesn't make sense. A better way for values in source would be the name - Iphone, web etc
# - Ratings (Numerator) only has intergers, it didn't included the decimal ratings.
# - Rating on (Denominator) doesn't include value less than 10 which is not correct.
# 
# - Names are sometimes preposition (a, an, the .. ). For tweet_id 666063827256086533 the name is **the**
# - Dog stages are not correct
# - Keep the same name of columns in both the all_tweet_clean and archive_clean
# - Extract rating from text into a new columns
# 
# `predictions_clean` **table**
# 
# - p1, p2, p3 have sometimes "-" and other times "_" between words
# - columns p1, p2 and p3 values have both lower and upper case
# 
# `all_tweet_clean` **table**
# 
# - Remove unwanted columns
# 
# ### Tidiness
# 
# - Merge data frames to get retweets and favorite counts
# - Dog stage are in different columns

# ## Cleaning

# ##### `archive_clean`: **Timestamp should be converted to datatime**
# 
# **Define:**
# 
# Convert the time-date from string to datetime
# 
# **Code:**

# In[36]:


archive_clean['timestamp'] = pd.to_datetime(archive_clean.timestamp)


# **Test**

# In[37]:


archive_clean.timestamp.describe()


# ##### `archive_clean`: **Remove retweeted tweets which are 181 of all the tweets**
# 
# **Define:**
# 
# Removing retweeted data. Keeping only direct tweets.
# 
# **Code:**

# In[38]:


archive_clean = archive_clean[archive_clean.retweeted_status_id.isnull()]


# **Test**

# In[39]:


archive_clean[archive_clean.retweeted_status_id.notnull()]


# ##### `archive_clean`: **Remove in reply to user id**
# 
# **Define:**
# 
# Not all reply tweets have rating in them. It's better to remove them.
# 
# **Code:**

# In[40]:


archive_clean = archive_clean[archive_clean.in_reply_to_status_id.isnull()]


# **Test**

# In[41]:


archive_clean[archive_clean.in_reply_to_status_id.notnull()]

