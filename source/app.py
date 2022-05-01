'''
Author: Austin Zang

Flask web app that provides a data retreival API from the SQLite database created by SQLite_database_creation.py

3 Endpoints, with optional parameters
'''


from flask import Flask, render_template, jsonify, request
from SQLite_database_creation import connect_to_sqlite_db
import os

app = Flask(__name__)

# GLOBAL VARIABLES
HTML_PATHS = r"./source/templates/" #path to html templates
DATABASE_PATH = r"./database/ign.db" #redfined database path for flask
ABS_DB_PATH = os.path.abspath(DATABASE_PATH) #absolute db path to smooth over SQLite3 performance bugs
print(ABS_DB_PATH)


@app.route("/")
def display_hub():
    """
    Displays the hub/index of API endpoints when routed to homepage

    Returns
    -------
    Flask render of html template
    """
    return render_template("index.html", template_folder=HTML_PATHS)


@app.route("/rating")
def fetch_ratings():
    """
    API endpoint to fetch movies by rating
    
    Optional GET request parameters: sortby = ASC | DESC (sort ratings by ascending or descending)

    Returns
    -------
    json response 
    """
    sorting = request.args.get('sortby', default = 'none', type = str)
    
    conn = connect_to_sqlite_db(ABS_DB_PATH)
    c = conn.cursor()
    
    if sorting == "ASC":
        data = c.execute("""
              SELECT name, review_score FROM media
              ORDER BY review_score ASC;
              """).fetchall()
    elif sorting == "DESC":
        data = c.execute("""
              SELECT name, review_score FROM media
              ORDER BY review_score DESC;
              """).fetchall()
    else: 
        data = c.execute("""
              SELECT name, review_score FROM media;
              """).fetchall()
    
    conn.close()
    
    return jsonify(data)


@app.route("/creator")
def fetch_types():
    """
    API endpoint to fetch creators and their work's ratings
    
    Optional GET request parameters: calculate = True | False (calculate avg studio rating)

    Returns
    -------
    json response 
    """
    calculate_avg = request.args.get('calculate', default = False, type=bool)
    
    conn = connect_to_sqlite_db(ABS_DB_PATH)
    c = conn.cursor()
    
    if calculate_avg:
        data = c.execute("""
                SELECT creator.creator, media.name, media.media_type, media.review_score, AVG(media.review_score) 
                OVER (PARTITION BY mediaCreators.creator_id) AS avg_studio_rating 
                FROM mediaCreators
                LEFT JOIN creator
                ON mediaCreators.creator_id = creator.creator_id
                LEFT JOIN media
                ON mediaCreators.media_id = media.id
                ORDER BY avg_studio_rating DESC;
                """).fetchall()
    else:
        data = c.execute("""
                SELECT creator.creator, media.name, media.media_type FROM mediaCreators
                LEFT JOIN creator
                ON mediaCreators.creator_id = creator.creator_id
                LEFT JOIN media
                ON mediaCreators.media_id = media.id
                ORDER BY creator ASC;
                """).fetchall()
    
    conn.close()
    
    return jsonify(data)
    
    
@app.route("/publisher")
def fetch_publisher():
    """
    API endpoint to fetch publishers and their work's associated genres
    
    Optional GET request parameters: calculate = True | False (calculate unique number of genres per publisher)

    Returns
    -------
    json response 
    """
    calculate_unique_genre = request.args.get('calculate', default = False, type=bool)
    
    conn = connect_to_sqlite_db(ABS_DB_PATH)
    c = conn.cursor()
    
    if calculate_unique_genre:
        data = c.execute("""
                    SELECT p.publisher, g.genre, count(*) OVER( PARTITION BY p.publisher) AS unique_genre_count
                    FROM mediaPublishers AS mp
                    LEFT JOIN publisher AS p
                    ON mp.publisher_id = p.publisher_id
                    LEFT JOIN media AS m
                    ON mp.media_id = m.id
                    INNER JOIN mediaGenres AS mg
                    ON mp.media_id = mg.media_id
                    INNER JOIN genre AS g
                    ON mg.genre_id = g.genre_id
                    ORDER BY unique_genre_count ASC;
                    """).fetchall()
    else:
        data = c.execute("""
                    SELECT p.publisher, g.genre
                    FROM mediaPublishers AS mp
                    LEFT JOIN publisher AS p
                    ON mp.publisher_id = p.publisher_id
                    LEFT JOIN media AS m
                    ON mp.media_id = m.id
                    INNER JOIN mediaGenres AS mg
                    ON mp.media_id = mg.media_id
                    INNER JOIN genre AS g
                    ON mg.genre_id = g.genre_id
                    ORDER BY p.publisher ASC;
                    """).fetchall()

    
    conn.close()
    return jsonify(data)