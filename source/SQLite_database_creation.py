
'''
Author: Austin Zang

Generates an SQLite3 database from given IGN foo csv file. Adheres to First Normal Form of database normalization, 
creating intermediary/junction tables to relate data that was originally inputted as a list 
'''

import sqlite3 as db
from sqlite3 import Error
import pandas as pd


# GLOBAL VARIABLES
RAW_CSV_PATH = r"./database/codefoobackend_cfgames.csv" #path to IGN-provided csv data
RELATIVE_DATABASE_PATH = r"./database/ign.db" #path to SQLite db file


def connect_to_sqlite_db(dbpath : str):
    """
    Establish connection to sqlite database

    Parameters
    ----------
    dbpath : str
        path to db

    Returns
    -------
    sqlite connection object
    """
    
    try:
        connection = db.connect(dbpath)
        print(f"SQLITE CONNECTION SUCCESS. running sqlite version {db.version}")
        return connection
    except Error as e:
        print(f"SQLITE CONNECTION ERROR: {e}")
           
def load_dataframe(input_path : str): 
    """
    Load input csv into pandas dataframe

    Parameters
    ----------
    input_path : str
        path to csv

    Returns
    -------
    pandas dataframe
    """
    try:
        df = pd.read_csv(input_path)
        print("DATAFRAME LOADED")
        return df
    except Error as e:
        print(f"DATAFRAME LOAD ERROR: {e}")


def create_tables(connection) -> None:
    """
    Create all non-junction SQL tables

    Parameters
    ----------
    connection : sqlite connection
        connection to database to modify
    """
    c = connection.cursor()
    
    # main table of media
    c.execute('''
              CREATE TABLE IF NOT EXISTS media(
              id INTEGER PRIMARY KEY NOT NULL,
              media_type VARCHAR,
              name VARCHAR,
              short_name VARCHAR,
              long_description TEXT,
              short_description TEXT,
              created_at DATETIME,
              updated_at DATETIME,
              review_url TEXT,
              review_score DECIMAL(2,1),
              slug VARCHAR
              );
              ''')
    
    # table of genres
    c.execute('''
              CREATE TABLE IF NOT EXISTS genre(
                  genre_id INTEGER PRIMARY KEY,
                  genre VARCHAR UNIQUE
              );
              ''')
    
    # table of creators
    c.execute('''
              CREATE TABLE IF NOT EXISTS creator(
                  creator_id INTEGER PRIMARY KEY,
                  creator VARCHAR UNIQUE
              );
              ''')
    
    # table of publishers
    c.execute('''
              CREATE TABLE IF NOT EXISTS publisher(
                  publisher_id INTEGER PRIMARY KEY,
                  publisher VARCHAR UNIQUE
              );
              ''')
    
    # table of franchises
    c.execute('''
              CREATE TABLE IF NOT EXISTS franchise(
                  franchise_id INTEGER PRIMARY KEY,
                  franchise VARCHAR UNIQUE
              );
              ''')
    
    # table of regions
    c.execute('''
              CREATE TABLE IF NOT EXISTS region(
                  region_id INTEGER PRIMARY KEY,
                  region VARCHAR UNIQUE
              );
              ''')
    
    connection.commit()
    
def create_media_junction_tables(connection) -> None:
    """
    Create junction tables to turn all many-to-many relationships (between media and other tables: genre, creator, publisher, franchise, region) into one-to-many 

    Parameters
    ----------
    connection : sqlite connection
        connection to database to modify
    """
    c = connection.cursor()
    
    # junction table of mediaGenres
    c.execute('''
              CREATE TABLE IF NOT EXISTS mediaGenres(
                  junction_id INTEGER PRIMARY KEY,
                  media_id INTEGER,
                  genre_id INTEGER,
                  FOREIGN KEY(media_id) REFERENCES media(id),
                  FOREIGN KEY(genre_id) REFERENCES genre(genre_id)
              );
              ''')
    
    # junction table of mediaCreators
    c.execute('''
              CREATE TABLE IF NOT EXISTS mediaCreators(
                  junction_id INTEGER PRIMARY KEY,
                  media_id INTEGER,
                  creator_id INTEGER,
                  FOREIGN KEY(media_id) REFERENCES media(id),
                  FOREIGN KEY(creator_id) REFERENCES creator(creator_id)
              );
              ''')
    
    # junction table of mediaPublishers
    c.execute('''
              CREATE TABLE IF NOT EXISTS mediaPublishers(
                  junction_id INTEGER PRIMARY KEY,
                  media_id INTEGER,
                  publisher_id INTEGER,
                  FOREIGN KEY(media_id) REFERENCES media(id),
                  FOREIGN KEY(publisher_id) REFERENCES publisher(publisher_id)
              );
              ''')
    
    # junction table of mediaFranchises
    c.execute('''
              CREATE TABLE IF NOT EXISTS mediaFranchises(
                  junction_id INTEGER PRIMARY KEY,
                  media_id INTEGER,
                  franchise_id INTEGER,
                  FOREIGN KEY(media_id) REFERENCES media(id),
                  FOREIGN KEY(franchise_id) REFERENCES franchise(franchise_id)
              );
              ''')
    
    # junction table of mediaRegions
    c.execute('''
              CREATE TABLE IF NOT EXISTS mediaRegions(
                  junction_id INTEGER PRIMARY KEY,
                  media_id INTEGER,
                  region_id INTEGER,
                  FOREIGN KEY(media_id) REFERENCES media(id),
                  FOREIGN KEY(region_id) REFERENCES region(region_id)
              );
              ''')
    
    connection.commit()
    

def view_all_tables(connection) -> None:
    """
    Print the names of all tables currently in db

    Parameters
    ----------
    connection : sqlite connection
        connection to database
    """
    
    c = connection.cursor()


    c.execute("SELECT name FROM sqlite_master WHERE type='table';")

    print(c.fetchall())
    
    
def iterate_dataframe(connection, dataframe) -> None:
    """
    Iterate through given dataframe and load data into database's SQL tables, including junction tables

    Parameters
    ----------
    connection : sqlite connection
        connection to db 

    dataframe : pandas dataframe
        dataframe to iterate through
        
    """
    c = connection.cursor()
    
    for index, row in dataframe.iterrows():
        
        insertion_tuple = (row["id"], row["media_type"], row["name"], row["short_name"], row["long_description"], 
                           row["short_description"], row["created_at"], row["updated_at"], 
                           row["review_url"], float(row["review_score"]), row["slug"])
        
        # --- Populate media table ---
        c.execute("""
                INSERT INTO media (id, media_type, name, short_name, long_description, 
                short_description, created_at, updated_at, review_url, review_score, slug) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                insertion_tuple
                )
        
        # ----- Populate Junction table and lookup table for Genre -----
        # Convert from string representation to python list 
        associated_genres = row["genres"].strip("{} ").split(",")
        if len(associated_genres) > 0:
            for genre in associated_genres:
                # flag to not add blank space entry 
                if genre == "" or genre == " ": break
                
                # insert genre into genre table 
                c.execute("""
                    INSERT OR IGNORE INTO genre (genre) VALUES (?)
                    """, ([genre])
                    )
                
                # get genre id of associated genre
                c.execute("""
                    SELECT genre_id FROM genre WHERE genre=(?)
                    """, ([genre])
                    )
                
                # get integer to store into variable
                current_genreID = c.fetchall()[0][0]
                
                # add to junction table
                c.execute("""
                    INSERT INTO mediaGenres (media_id, genre_id) VALUES (?,?)
                    """, (row["id"], current_genreID)
                    )
                
        # ----- Populate Junction table and lookup table for Creator -----
        associated_creators = row["created_by"].strip("{} ").split(",")
        if len(associated_creators) > 0:
            for creator in associated_creators:
                # flag to not add blank space entry 
                if creator == "" or creator == " ": break
                
                
                c.execute("""
                    INSERT OR IGNORE INTO creator (creator) VALUES (?)
                    """, ([creator])
                    )
                
                
                c.execute("""
                    SELECT creator_id FROM creator WHERE creator=(?)
                    """, ([creator])
                    )
                
                # get integer to store into variable
                current_creatorID = c.fetchall()[0][0]
                
                # add to junction table
                c.execute("""
                    INSERT INTO mediaCreators (media_id, creator_id) VALUES (?,?)
                    """, (row["id"], current_creatorID)
                    )
                
        # ----- Populate Junction table and lookup table for Publisher -----    
        associated_publishers = row["published_by"].strip("{} ").split(",")
        if len(associated_publishers) > 0:
            for publisher in associated_publishers:
                # flag to not add blank space entry 
                if publisher == "" or publisher == " ": break
                
                
                c.execute("""
                    INSERT OR IGNORE INTO publisher (publisher) VALUES (?)
                    """, ([publisher])
                    )
                
                
                c.execute("""
                    SELECT publisher_id FROM publisher WHERE publisher=(?)
                    """, ([publisher])
                    )
                
                # get integer to store into variable
                current_publisherID = c.fetchall()[0][0]
                
                # add to junction table
                c.execute("""
                    INSERT INTO mediaPublishers (media_id, publisher_id) VALUES (?,?)
                    """, (row["id"], current_publisherID)
                    )
                
        
        # ----- Populate Junction table and lookup table for Franchise -----           
        associated_franchises = row["franchises"].strip("{} ").split(",")
        if len(associated_franchises) > 0:
            for franchise in associated_franchises:
                # flag to not add blank space entry 
                if franchise == "" or franchise == " ": break
                
                
                c.execute("""
                    INSERT OR IGNORE INTO franchise (franchise) VALUES (?)
                    """, ([franchise])
                    )
                
                
                c.execute("""
                    SELECT franchise_id FROM franchise WHERE franchise=(?)
                    """, ([franchise])
                    )
                
                # get integer to store into variable
                current_franchiseID = c.fetchall()[0][0]
                
                # add to junction table
                c.execute("""
                    INSERT INTO mediaFranchises (media_id, franchise_id) VALUES (?,?)
                    """, (row["id"], current_franchiseID)
                    )
                
        # ----- Populate Junction table and lookup table for Region -----  
        if "{" in str(row["regions"]):
            associated_regions = str(row["regions"]).strip("{} ").split(",")
        
            if len(associated_regions) > 0:
                for region in associated_regions:
                    # flag to not add blank space entry 
                    if region == "" or region == " ": break
                    
                    
                    c.execute("""
                        INSERT OR IGNORE INTO region (region) VALUES (?)
                        """, ([region])
                        )
                    
                    
                    c.execute("""
                        SELECT region_id FROM region WHERE region=(?)
                        """, ([region])
                        )
                    
                    # get integer to store into variable
                    current_regionID = c.fetchall()[0][0]
                    
                    # add to junction table
                    c.execute("""
                        INSERT INTO mediaRegions (media_id, region_id) VALUES (?,?)
                        """, (row["id"], current_regionID)
                        )
        
    connection.commit()
            
if __name__ == '__main__':
    
    # establish connection to ign db
    ign_conn = connect_to_sqlite_db(RELATIVE_DATABASE_PATH)
    
    # load into pd dataframe
    ign_df = load_dataframe(RAW_CSV_PATH)
    
    # create necessary data tables
    create_tables(ign_conn)
    
    # create necessary media junction tables
    create_media_junction_tables(ign_conn)
    
    
    # view all existing tables
    view_all_tables(ign_conn)
    
    # iterate through df, populate tables
    iterate_dataframe(ign_conn, ign_df)
    
    # pretty print media table for sanity check
    print(pd.read_sql_query("SELECT * FROM media", ign_conn))
    
    # close connection
    ign_conn.close()
    
    
    


    
    