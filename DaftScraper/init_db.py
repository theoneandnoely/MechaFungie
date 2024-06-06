import sqlite3
from os.path import exists

def init_db() -> None:
    '''
    Initialises the daft_data.db database with the campaigns and properties tables and correct columns

    INPUT:
    None

    OUTPUT:
    None
    '''
    # Raise error if database already exists, create and connect otherwise
    if exists('daft_data.db'):
        raise RuntimeError('Tried to Initialise Database which already exists.')
    conn = sqlite3.connect('daft_data.db')
    curs = conn.cursor()

    # Create campaigns table with columns for campaign ID, number of beds for campaign, max price for campaign, and which user(s) to mention in post
    curs.execute("CREATE TABLE campaigns (id INTEGER PRIMARY KEY, num_beds INTEGER, max_price INTEGER, mentions TEXT, active INTEGER);")

    # Create properties table with columns for the daft ID, number of beds in property, price in ad, latitude, and longitude of property
    curs.execute("CREATE TABLE properties (daft_id TEXT, link TEXT, address TEXT, img_url TEXT, num_beds INTEGER, price REAL, latitude REAL, longitude REAL);")

    curs.close()
    conn.close()

if __name__ == '__main__':
    init_db()