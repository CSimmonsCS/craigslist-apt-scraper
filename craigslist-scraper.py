from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
from requests import get
import numpy as np
from time import sleep
from random import randint
from warnings import warn

# get the base URL for SF apartments on craigslist
# Has at least one photo

BASE_URL = 'https://sfbay.craigslist.org/search/sfc/apa?hasPic=1&availabilityMode=0'
response = get(BASE_URL)
sleep(5)

# Using BeautifulSoup to make scraping HTML easier
html_soup = BeautifulSoup(response.text, 'html.parser')

# print(html_soup.prettify())

# get where the housing posts live on the page
posts = html_soup.find_all("li", "result-row")

# check how many results
# should be 120 max
# print(len(posts))

# print(posts[0].prettify())

first_post = posts[0]
# print(type(first_post))

# getting price
price_first_post = first_post.find('span', class_="result-price").text
price_first_post.strip()
# print(price_first_post)

# getting date posted
datetime_first_post = first_post.find('time', class_="result-date")['datetime']
# print(datetime_first_post)

# getting housing
housing_first_post = first_post.find('span', class_="housing")
if housing_first_post is not None:
    housing_first_post = housing_first_post.text.split()
    # br_first_post = housing_first_post[0]
    # sqft_first_post = housing_first_post[2]
# housing_first_post.strip()
    # print(housing_first_post)
    # print(br_first_post)
    # print(sqft_first_post)

    '''
    FIGURE OUT HOW TO HANDLE ERROR IF NO BEDROOM OR SQUARE FT
    '''

    # check if first post is bedroom
    # if first post is bedroom, check if square feet is entered
    # if first post is not bedroom, then there is no second term
    # br_first_post = housing_first_post[0]

    if housing_first_post[0][-1] == 'r':
        br_first_post = housing_first_post[0]

        if housing_first_post[-1] != '-':
            sqft_first_post = housing_first_post[2]
        else:
            sqft_first_post = 'NA'

    elif housing_first_post[0][-1] == '2':
        br_first_post = 'NA'
        sqft_first_post = housing_first_post[0]

    # print(br_first_post)
    # print(sqft_first_post)

else:
    print('no text')

# getting neighborhood
hood_first_post = first_post.find('span', class_="result-hood").text
# print(hood_first_post)

#getting title of post
title_first_post = first_post.find('a', class_="result-title").text
# print(title_first_post)

'''
Creating for loop to get all 120 posts on page
'''

# all arrays initiated here
prices = []
datetimes = []
hoods = []
titles = []
brs = []
sqfts = []


def dataAllPosts():

    '''
    CREATE HOW TO GET FOR EACH PAGE
    If page does not return respone 200,
    we are done
    '''

    # get total number of posts by finding <span> with class of 'totalcount'
    total_num_results = int(html_soup.find('span', class_='totalcount').text)
    print(total_num_results)

    # creates a range from 0 - total_num_results incremented by 120 (0, 120, 240, etc)
    num_pages = np.arange(0, total_num_results+1, 120)

    iterations = 0

    # iterate through each page 'num' in num_pages and each post on the page
    for page in num_pages:
        print(page)
        pageURL = 'https://sfbay.craigslist.org/d/apartments-housing-for-rent/search/sfc/apa?' + 's=' + str(page) + '&hasPic=1' + '&availabilityMode=0'

        # error handling because we would get connection refused after many requests
        try:
            response = get(pageURL)
        except:
            print('connection refused')
            continue

        sleep(randint(5,10))
        #this is so we do not throttle by sending too many requests

        # print(response.status_code)

        if response.status_code != 200:
            warn('Request: {}; Status Code: {}'.format(requests, response.status_code))

        page_html = BeautifulSoup(response.text, 'html.parser')

        posts = page_html.find_all("li", "result-row")

        # gets all the data from one post
        for post in posts:

            if post.find('span', class_="result-hood") is not None:

                # prices & datetimes are easily appended to arrays
                PRICE = post.find('span', class_="result-price").text.strip()
                DATETIME = post.find('time', class_="result-date")['datetime']
                NEIGHBORHOOD = post.find('span', class_="result-hood").text
                TITLE = post.find('a', class_="result-title").text

                prices.append(PRICE)
                datetimes.append(DATETIME)
                hoods.append(NEIGHBORHOOD)
                titles.append(TITLE)

                # bedrooms & square footage if statements
                # check if housing span is present
                if post.find('span', class_="housing") is not None:
                    # split housing span into array
                    housing_post = post.find('span', class_="housing").text.split()
                    len_housing_post = len(housing_post)

                    # check if bedroom is inputted
                    if housing_post[0][-1] == 'r':
                        brs.append(housing_post[0])

                        # take square footage if present
                        if (housing_post[-1] != '-' and len_housing_post == 3) or (len_housing_post == 4):
                            sqfts.append(housing_post[2])
                        else:
                            sqfts.append('NA')

                    # else check if square footage is first
                    elif housing_post[0][-1] == '2':
                        brs.append('NA')
                        sqfts.append(housing_post[0])

                    else:
                        print('Nothing input')
                # no bedrooms or square footage added
                else:
                    # print('no br or sqft')
                    sqfts.append('NA')
                    brs.append('NA')
        iterations = iterations + 1

        print("Page " + str(iterations) + " scraped successfully!")

    print('Successful Scrape')

dataAllPosts()
print(len(prices))
print(len(datetimes))
print(len(hoods))
print(len(titles))
print(len(brs))
print(len(sqfts))

sfc_apts = pd.DataFrame(({'posted': datetimes,
                       'neighborhood': hoods,
                       'post title': titles,
                       'number bedrooms': brs,
                        'sqft': sqfts,
                        # 'URL': post_links,
                       'price': prices}))

print(sfc_apts.info())
sfc_apts.head(10)

#first things first, drop duplicate titles because people are spammy on Craigslist.
#Let's see how many uniqe posts we really have.
sfc_apts = sfc_apts.drop_duplicates(subset='post title')

# make the number bedrooms to a float (since np.nan is a float too)
sfc_apts['number bedrooms'] = sfc_apts['number bedrooms'].apply(lambda x: float(x))

#convert datetime string into datetime object to be able to work with it
from datetime import datetime

sfc_apts['posted'] = pd.to_datetime(sfc_apts['posted'])

#Looking at what neighborhoods there are with sfc_apts['neighborhood'].unique() allowed me to see what
#I needed to deal with in terms of cleaning those.

#remove the parenthesis from the left and right of the neighborhoods
sfc_apts['neighborhood'] = sfc_apts['neighborhood'].map(lambda x: x.lstrip('(').rstrip(')'))

#titlecase them
sfc_apts['neighborhood'] = sfc_apts['neighborhood'].str.title()

#just take the first name of the neighborhood list, splitting on the '/' delimiter
sfc_apts['neighborhood'] = sfc_apts['neighborhood'].apply(lambda x: x.split('/')[0])

#fix one-offs that
# sfc_apts['neighborhood'].replace('Belmont, Ca', 'Belmont', inplace=True)
# sfc_apts['neighborhood'].replace('Hercules, Pinole, San Pablo, El Sob', 'Hercules', inplace=True)

#remove whitespaces
sfc_apts['neighborhood'] = sfc_apts['neighborhood'].apply(lambda x: x.strip())

#save the clean data
sfc_apts.to_csv("sfc_apts_1642_Jan_2_19_clean.csv", index=False)

'''
NEED TO CLEAN DATA CORRECTLY!!!
'''
