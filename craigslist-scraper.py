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
    
else:
    print('no text')

# getting neighborhood
hood_first_post = first_post.find('span', class_="result-hood").text
print(hood_first_post)
