# IGNfoo

## SQL Database Creation
Given the csv data, we see that the First Normal Form of relational databases is violated, as several columns (genres, published_by, region, etc.) contain composite/multi-valued data.
- I normalize the database by breaking the many-to-many relationships between media and these multi-valued columns: intermediary/junction tables are created to relate several independent tables instead

The main media table was indexed by the existing id value within the csv.
Every other table is indexed by an auto-incrementing integer primary key, indentifying an unique ID value for that table. 
Junction tables utilize two foreign keys - each referencing the primary key id values of the related tables

In theory, columns containing small strings were typed as VARCHAR to potentially support faster database searching, but SQLite does not differentiate from TEXT.

For query construction, I used SQLite's built-in parameterized queries (with "?" value substitution) instead of string concatenation to ensure safety against SQL injection vulnerability.





## API Endpoint Creation

## Use
Ensure python packages outlined in requirements.txt are installed (```venv``` recommended)

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
Alternatively, ```cd``` into```/source``` and execute ```flask run```.

#### API
Available endpoints are directly linked to on the flask app's index page. URLs are also listed above. All endpoints deliver data in json format. 

#### Database Creation
Existing SQLite database is already included (```ign.db```), but if a new db needs to be generated simply run ```SQLite_database_creation.py```. Script assumes raw csv file is in database directory for reading.





