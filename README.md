# UPA project
This project is dealing with COVID-19 data storage, processing and analysis.

Authors:
 - xberan46@stud.fit.vutbr.cz
 - xkamen21@stud.fit.vutbr.cz
 - xklemr00@stud.fit.vutbr.cz

## Prerequisites
 - Fully set up MongoDB - could be on-premise or cloud solution. Use<br>
corresponding connection methods in file `src/loader.py`.
 - Python 3.8 with pip module.
 - It is recommended (not mandatory) to use virtual environment.
 
### Install requirements
`pip install -r requirements.txt`

### MongoDB secrets
There is available a distribution (.dist) version of MongoDB secrets called<br>
`mongo_secrets.py.dist`. Copy this file as `mongo_secrets.py` and fill with<br>
your own data (preferred). Alternatively you can change the source code of the<br>
`load_data` function in `loader.py`.

## Run the code
Use `python3 main.py` or `make` to run the downloading and inserting into DB.

To clean up the project, type `make clean`.

If you want to run the **whole** process from the beginning again, you must<br>
delete all data files from your data folder and delete all collections from<br>
the database. 

## Behaviour of the script
It is expected that this code is run to set up the whole database from scratch.<br>
That means that if there is already CSV file with the specified name, the new one<br>
is not downloaded, same for the JSON files and data processing. If there is<br>
a collection in DB which has the specified name, no new data will be inserted.<br>
In manor of rewrite the collection, you must delete the collection and run the<br>
script again.

## About source code
## Constants `data_files.py`
This file is used as dynamic approach to the constants like data file names<br>
their sets of columns which are required for our analysis and their base URLs.

## Credential file `mongo_secrets.py`
You must create this file as copy of `mongo_secrets.py.dist`. It is used for<br>
storing database connection secrets,

### Class `DataHandler`
This class can download data files from specified web-pages and store them<br>
in the data folder (default is `<project_root>/data` folder). <br>

### Function `load_data`
This function connects to the specified MongoDB database and insert data in a<br>
collection named by data file name.

Something more you can read in our documentation located at this