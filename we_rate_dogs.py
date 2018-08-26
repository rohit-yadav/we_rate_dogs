
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

