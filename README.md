# IGNfoo
Austin Zang
IGN Code Foo X Submission - Backend
<br>
Look in "source" directory for code!

python3, flask, sqlite3, pandas
## SQL Database Creation

#### Normalization
Given the csv data, we see that the First Normal Form of relational databases is violated, as several columns (genres, published_by, region, etc.) contain composite/multi-valued data.
- I normalize the database by breaking the many-to-many relationships between media and these multi-valued columns: intermediary/junction tables are created to relate several independent tables instead

#### Indexing and Table Construction

The main media table was indexed by the existing id value within the csv.
Every other table is indexed by an auto-incrementing integer primary key, indentifying an unique ID value for that table. 
Junction tables utilize two foreign keys - each referencing the primary key id values of the related tables

In theory, columns containing small strings were typed as ```VARCHAR``` to potentially support faster database searching, but SQLite does not differentiate from ```TEXT```.
Timestamp data points were inserted into columns typed as ```DATETIME```.

I created an index for the ```media.name``` column, as in practical use it's likely to be included in many ```WHERE``` clauses, and contains text. Indexing it now will speed up future queries and joins.


All database table operations (table creation, data insertion, query) are done with sqlite3's ```cursor.execute()```  paired with raw SQL syntax. 

- Data insertion was done by iterating row-by-row through a dataframe of the csv, inserting relevant data points into both regular and junction tables. 
- Tables that tracked non-repeating data (like all the genres represented in the csv) were given the ```UNIQUE``` constraint

#### Security 
For query construction, I used SQLite's built-in parameterized queries (with "?" value substitution) instead of string concatenation to ensure safety against SQL injection vulnerability.





## API Endpoint Creation
Data fetching API service is provided through a locally-running Flask application. 
- The local flask app establishes a connection to the previously created SQLite database and executes SQL queries based on endpoint
- Flask's built-in  ```jsonify``` method is used to convert the results of SQL query into a returnable JSON response


#### Endpoints and optional parameters:
```/rating```
Uses media table to fetch media names and associated review scores.
 - ```/rating?sortby=ASC```
 -- Changes SQL ```ORDER BY``` parameter to sort review score by ascending
 - ```/rating?sortby=DESC```
  -- Changes SQL ```ORDER BY``` parameter to sort review score by descending

```/creator```
Uses mediaCreators junction table and two ```LEFT JOIN``` to connect creators with associated works and review scores
- ```/creator?calculate=True```
-- Additionally uses window function  (```AVG()```, partitioned by creator id) to calculate average review scores of each studio (average rating of all of their works)

```/publisher```
Uses mediaPublishers junction table and two ```LEFT JOIN```, as well as mediaGenres junction table and two  ```INNER JOIN```. Connect publishers with all the genres they've produced works in (must relate publishers with media, then media with genres).
- ```/publisher?calculate=True```
-- Additionally uses window function  (```SUM(*)```, partitioned by publisher name) to calculate the number of unique genres published by each publisher

<br>

URL parameters are fetched from HTTPS GET requests with Flask's built-in ```request.args.get``` method.

## Use
Install python packages outlined in requirements.txt (```venv``` recommended)

### With terminal open in the project's root directory, run the following:
#### Unix BASH/ZSH
```
$ export FLASK_APP=source/app
$ flask run
```

#### Windows CMD
```
> set FLASK_APP=source/app
> flask run
```

#### API
Available endpoints are directly linked to on the flask app's index page. URLs are also listed above. All endpoints deliver data in json format. 

#### Database Creation
Existing SQLite database is already included (```ign.db```), but if a new db needs to be generated simply run ```SQLite_database_creation.py```. Script assumes raw csv file is in database directory for reading.



## Bonus Media
Screenshot of DB structure (viewed with DB Browser for SQLite)

![Screenshot of DB structure, viewed with DB Browser](./assets/Schema.PNG?raw=true)
![index](./assets/Index.PNG?raw=true)
![response](./assets/json.PNG?raw=true)


