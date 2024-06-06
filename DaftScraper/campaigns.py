import sqlite3
import pandas as pd
from typing import List
from os.path import exists
from DaftScraper.init_db import init_db

def add_campaign(num_beds:int, max_price:float, mentions:List[str]) -> int:
    '''
    Add a new campaign to the database

    INPUT:
    num_beds (int): the minimum number of beds required for properties to be considered in this campaign
    max_price (float): the maximum monthly rent for properties to be considered in this campaign
    mentions (list): the list of users to be @ mentioned in posts for this campaign

    OUTPUT:
    id: the id of the newly added campaign
    '''
    # Initialise DB if not already existing
    if exists('daft_data.db') == False:
        init_db()
        print('Database initialisesd!')

    # Convert mention list into semicolon delimited list
    mention_list = ";".join([str(x) for x in mentions])
    
    conn = sqlite3.connect('daft_data.db')
    
    # Pull existing campaigns table from DB
    df = pd.read_sql_query("SELECT * FROM campaigns;", conn)

    # If the table is empty, create pandas DataFrame with one row containing new campaign details, else append the campaign to existing campaigns table
    if len(df['id']) == 0:
        id = 1
        df = pd.DataFrame([[id, num_beds, max_price, mention_list, 1]], columns=['id', 'num_beds', 'max_price', 'mentions', 'active'])
    else:
        id = df['id'].max() + 1
        df = pd.concat([df, pd.DataFrame([[id, num_beds, max_price, mention_list, 1]], columns=['id','num_beds','max_price','mentions', 'active'])], ignore_index=True)

    # Replace campaigns table in DB with new campaigns table
    df.to_sql('campaigns', conn, if_exists='replace', index=False)
    conn.close()
    return id

def deactivate_campaign(id:int) -> None:
    '''
    Update the campaign with the given ID to have an active value of 0 in the db.

    INPUT:
    id (int): the id in the database for the campaign you wish to deactivate

    OUTPUT:
    None
    '''
    # Flag error if database not initialised
    if exists('daft_data.db') == False:
        raise RuntimeError('Database does not exist')

    # Connect to DB and create cursor objec
    conn = sqlite3.connect('daft_data.db')
    curs = conn.cursor()

    # Use UPDATE command to set the active field to 0 for the given ID, execute the query and commit it to the DB
    query = f'UPDATE campaigns SET active = 0 WHERE id = {id};'
    curs.execute(query)
    conn.commit()

    # Closin' Time
    curs.close()
    conn.close()

def active_campaigns() -> List[List]:
    '''
    Return the list of currently active DaftScrape campaigns

    INPUT:
    None

    OUTPUT:
    ids (list): list of the ids of active campaigns
    beds (list): list of the num_beds values for the active campaigns
    price (list): list of the max_price values for the active campaigns
    '''
    # Flag error if DB not initialised
    if exists('daft_data.db') == False:
        raise RuntimeError("Database not initialised")
    
    # Connect to DB and use pandas to return the id, num_beds, and max_price fields as a DataFrame object then close connection
    conn = sqlite3.connect('daft_data.db')
    df = pd.read_sql_query('SELECT id, num_beds, max_price FROM campaigns WHERE active = 1;', conn)
    conn.close()
    
    # Convert the Series to list objects and return as a list for use in discord command
    return [list(df['id']), list(df['num_beds']), list(df['max_price'])]

if __name__ == '__main__':
    ids, beds, prices = active_campaigns()
    print(f'IDs: {ids}\nBeds: {beds}\nPrices: {prices}')