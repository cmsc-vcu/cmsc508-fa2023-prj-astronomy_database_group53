from flask import Flask, request, jsonify
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

def db_connection():
    # modify config_map to reflect credentials needed by this program
    config_map = {
        'user':'CMSC508_USER',
        'password':'CMSC508_PASSWORD',
        'host':'CMSC508_HOST',
        'database':'ASTRONOMY_DB_NAME'
    }

    # load and store credentials
    load_dotenv()
    config = {}
    for key in config_map.keys():
        config[key] = os.getenv(config_map[key])

    # build a sqlalchemy engine string
    engine_uri = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}/{config['database']}"

    # create a database connection
    try:
        cnx = create_engine(engine_uri)
    except Exception as e:
        print(f"create_engine: An error occurred: {e}")
        return 1
    return cnx
        
app = Flask(__name__)

@app.route('/')
def index():
    return "welcome"

@app.route('/observers', methods=['GET'])
def show_observers():
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from observers
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    # format data returned
    df = df.to_dict()
    observer = {}
    observers = []
    i = 0
    while i < len(df['first_name']):
        first_name = df['first_name'][i]
        last_name = df['last_name'][i]
        observer['observer_id'] = i
        observer['first_name'] = first_name
        observer['last_name'] = last_name
        observers.append(observer)

    # if data exists, return it is JSON
    if observers is not None:
        return jsonify({'observers' : f'{observers}'})
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/events', methods=['GET'])
def show_events():
    pass

@app.route('/objects', methods=['GET'])
def show_objects():
    pass

if __name__ == "__main__":
    app.run()
