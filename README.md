# swimwiththefishes
Python 2.7 compatible

# CLI
Can be run with main.py -s for an intital setup with pulling of the ips from the text file, followed by all the geoip and rdap lookups.

Can also be run with main.py -q to run a query on the data. Use of the query language is described below.

# Running a query

When run with main.py -q will ask the user for a query.
Language is structured as such.
All queries are case sensitive, must start with *s which acts as a Select similar to SQL. This tells the program which columns to select so *S ip, city will only select the ip and city columns. There is a * operator which will select all columns ex: *S *

