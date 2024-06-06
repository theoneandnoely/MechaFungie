from bs4 import BeautifulSoup
import requests
from typing import List
from dotenv import load_dotenv
from os import getenv
from os.path import exists
import json
import sqlite3
import pandas as pd

def get_coords(address:str) -> List[float]:
    '''
    Uses positionstack.com API to determine latitude and longitude from coordinates based on the address in the daft ad.

    INPUT:
    - address (str): The address from the daft ad

    OUPUT:
    - latitude (float): Degrees North of the equator as a float (negative numbers equal south of equator)
    - longitude (float): Degress East of Prime Meridian as float (negative numebers equal west of Prime Meridian)
    '''
    load_dotenv()
    api_key = getenv('POS_STACK_KEY')
    url = f'http://api.positionstack.com/v1/forward?access_key={api_key}&query={address}&country=IE&region=Dublin&fields=results.latitude,results.longitude'

    with requests.get(url) as response:
        data = json.loads(response.text)

    if len(data["data"]) == 0:
        print(f'No coordinates found for {address}.')
        altered_address = address.split(',')[1]
        url = f'http://api.positionstack.com/v1/forward?access_key={api_key}&query={altered_address}&country=IE&region=Dublin&fields=results.latitude,results.longitude'
        with requests.get(url) as response:
            data = json.loads(response.text)
        if len(data["data"]) == 0:
            print(f'No coordinates found for {altered_address} either.')
            return(0,0)
        else:
            return data["data"][0]["latitude"], data["data"][0]["longitude"]
    else:
        return data["data"][0]["latitude"], data["data"][0]["longitude"]

def scrape_daft(campaign_id, num_beds, max_price) -> List[dict]:
    '''
    Scrapes the daft website for ads fitting the given criteria and returns a list of dictionaries containing the id, url, address, thumbnail url, price, latitude, and longitude for each new ad.
    The list will return the details of up to the 10 newest properties that do not exist in the properties table of the database.

    INPUT:
    - campaign_id (int): The ID for the campaign
    - num_beds (int): The minimum number of beds for the properties to be searched
    - max_price (int): The maximum monthly rent to filter the properties by

    OUTPUT:
    - properties (list): A list of dictionaries for each property scraped. Each dictionary contains the id, url, address, thumbnail url, price, latitude, and longitude of the property.
    '''
    # Format url to filter the search to the relevant properties
    url = f'https://www.daft.ie/property-for-rent/dublin-city?rentalPrice_to={str(max_price)}&numBeds_from={str(num_beds)}&sort=publishDateDesc'
    with requests.get(url) as page:
        soup = BeautifulSoup(page.text, "html.parser")
    
    # Get the list of the properties from the returned html
    results = soup.find('ul', attrs={'data-testid':'results'})

    properties = []
    counter = 0

    for list_item in results.find_all('li'):
        # Pull the specific data from the html
        id = list_item['data-testid']
        link = list_item.find('a').get('href')
        address = list_item.find('p', attrs={"data-testid":"address"}).text
        price = list_item.find('div', attrs={"data-testid":"price"}).h3.text
        img_url = list_item.find('img').get('src')

        # Exit scrape after 10 properties
        if counter == 10:
            return properties
        else:
            # Exit scrape if id is already in database
            existing_id = pd.read_sql_query(f'SELECT daft_id FROM properties WHERE daft_id="{id}";')
            if len(existing_id['daft_id']) > 0:
                return properties
            # Get the latitude and longitude from Position stack
            lat, lon = get_coords(address)
            # Create the dictionary for the property and append it to the output list
            properties.append(
                {
                    'daft_id':id, 
                    'link':f'https://www.daft.ie{link}', 
                    'address':address, 
                    'img_url':img_url, 
                    'num_beds':num_beds,
                    'price':price, 
                    'latitude':lat, 
                    'longitude':lon
                }
            )
            counter += 1
    return properties

def update_properties(daft_id:str, link:str, address:str, img_url:str, num_beds:int, price:str, lat:float, lon:float) -> None:
    '''
    Add record to the db for a single property.

    INPUT:
    - daft_id (str): The id for the property on daft
    - link (str): The url to the ad on daft
    - address (str): The address as shown in the ad on daft
    - img_url (str): The url for the thumbnail shown in the ad on daft
    - price (str): the '€xxx per month' or '€xxx per week' price noted on the ad on daft
    - lat (float): the latitude of the property pulled from position stack
    - lon (float): the longitude of the property pulled from position stack

    OUTPUT:
    None
    '''
    # Convert Price from string to float, normalised to a monthly price
    if 'week' in price:
        price_flt = (float(price.split('€')[1].split(' ')[0].replace(',',''))*52)/12
    else:
        price_flt = float(price.split('€')[1].split(' ')[0].replace(',',''))

    # Raise error if db doesn't exist, otherwise connect to db
    if exists('daft_data.db') == False:
        raise RuntimeError('Database not initialised')
    
    conn = sqlite3.connect('daft_data.db')
    curs = conn.cursor()

    values = f'("{daft_id}", "{link}", "{address}", "{img_url}", {num_beds}, {price_flt}, {lat}, {lon})'

    curs.execute(f'INSERT INTO properties (daft_id, link, address, img_url, num_beds, price, latitude, longitude) VALUES {values};')
    conn.commit()

    curs.close()
    conn.close()