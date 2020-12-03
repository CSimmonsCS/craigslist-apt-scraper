from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
from requests import get

# get the base URL for SF apartments on craigslist
# Has at least one photo

BASE_URL = 'https://sfbay.craigslist.org/search/sfc/apa?hasPic=1&availabilityMode=0&sale_date=all+dates'
response = get(BASE_URL)

# Using BeautifulSoup to make scraping HTML easier
html_soup = BeautifulSoup(response.text, 'html.parser')

# print(html_soup.prettify())

# get where the housing posts live on the page
posts = html_soup.find_all("li", "result-row")

# check how many results
# should be 120 max
print(len(posts))

# print(posts[0].prettify())

first_post = posts[0]
print(type(first_post))

# getting price
price_first_post = first_post.find('span', class_="result-price").text
price_first_post.strip()
print(price_first_post)

# getting date posted
datetime_first_post = first_post.find('time', class_="result-date")['datetime']
print(datetime_first_post)

# getting housing
housing_first_post = first_post.find('span', class_="housing")
if housing_first_post is not None:
    housing_first_post = housing_first_post.text.split()
    # br_first_post = housing_first_post[0]
    # sqft_first_post = housing_first_post[2]
# housing_first_post.strip()
    print(housing_first_post)
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

        if housing_first_post[2]:
            sqft_first_post = housing_first_post[2]
        else:
            sqft_first_post = 'NA'

    elif housing_first_post[0][-1] == '2':
        br_first_post = 'NA'
        sqft_first_post = housing_first_post[0]

    print(br_first_post)
    print(sqft_first_post)

else:
    print('no text')

# getting neighborhood
hood_first_post = first_post.find('span', class_="result-hood").text
print(hood_first_post)

#getting title of post
title_first_post = first_post.find('a', class_="result-title").text
print(title_first_post)

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

def dataAllPosts(posts):

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

                # check if bedroom is inputted
                if housing_post[0][-1] == 'r':
                    brs.append(housing_post[0])

                    # take square footage if present
                    if housing_post[-1] != '-':
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
                sqfts.append('NA')
                brs.append('NA')

dataAllPosts(posts)
print(len(prices))
print(len(datetimes))
print(len(hoods))
print(len(titles))
print(len(brs))
print(len(sqfts))
