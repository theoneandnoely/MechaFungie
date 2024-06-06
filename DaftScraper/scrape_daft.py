from bs4 import BeautifulSoup
import requests
from typing import List
from dotenv import load_dotenv
from os import getenv
from os.path import exists
import json

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

def scrape_daft(campaign_id, num_beds, max_price):

    url = f'https://www.daft.ie/property-for-rent/dublin-city?rentalPrice_to={max_price}&numBeds_from={num_beds}&sort=publishDateDesc'
    with requests.get(url) as page:
        soup = BeautifulSoup(page.text, "html.parser")
    
    results = soup.find('ul', attrs={'data-testid':'results'})

    properties = []
    counter = 0

    for list_item in results.find_all('li'):

        id = list_item['data-testid']
        link = list_item.find('a').get('href')
        address = list_item.find('p', attrs={"data-testid":"address"}).text
        price = list_item.find('div', attrs={"data-testid":"price"}).h3.text
        img_url = list_item.find('img').get('src')

        if counter == 10:
            return properties
        else:
            lat, lon = get_coords(address)
            properties.append(
                {
                    'daft_id':id, 
                    'link':f'https://www.daft.ie{link}', 
                    'address':address, 
                    'img_url':img_url, 
                    'price':price, 
                    'latitude':lat, 
                    'longitude':lon
                }
            )
            counter += 1
    return properties