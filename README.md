# swimwiththefishes
Python 2.7 compatible

# CLI
Can be run with main.py -s for an intital setup with pulling of the ips from the text file, followed by all the geoip and rdap lookups.

Can also be run with main.py -q to run a query on the data. Use of the query language is described below.

# Running a query

When run with main.py -q will ask the user for a query.
Language is structured as such.
All queries are case sensitive, must start with *s which acts as a Select similar to SQL. This tells the program which columns to select so *S ip, city will only select the ip and city columns. There is a * operator which will select all columns ex: *S *

The next operator in the language is *W which acts as the where conditional of this language.

You can then do *S * *W (city=Denver)
This will select all columns and rows where the city is Denver.
In the Where conditional you can have =, !=, and *I. *I acts as an in operator allowing you to put in a list of values to be matched on.
For example *S ip *W (city*IDenver, Chicago, Dallas) Will select all the ips where the city matches either Denver, or Chicago, or Dallas.

There is also the *A which is the AND conditional and *O which acts as the OR conditional to specify your searches more or combine based on different criteria.

For example *S * *W (city*IChicago, Dallas) *O (region_code=CO) *A (city!=Denver)
Will select all keys where the city is either Chicago and Dallas OR where the state is CO but the city is not Denver.

You only ever need one *W followed by as many *A and/or *O conditionals you want.
