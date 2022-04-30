# IGNfoo

## SQL Database Creation
Given the csv data, we see that the First Normal Form of relational databases is violated, as several columns (genre, publisher, region, etc.) contain composite/multi-valued data.
- I normalize the database by breaking the many-to-many relationships between media and these multi-valued columns: intermediary/junction tables are created to relate several independent tables instead

The media table was indexed by the existing id value within the csv.
Each other table is indexed by an auto-incrementing integer primary key, indentifying an unique ID value for that table. 
Junction tables utilize two foreign keys - each referencing the primary key id values of the joined tables

In theory, columns containing small strings were assigned VARCHAR to support faster database searching, but I believe SQLite does not 


## API Endpoint Creation
