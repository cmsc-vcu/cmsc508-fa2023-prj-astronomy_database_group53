from flask import Flask, request, jsonify
import os
import pandas as pd
from sqlalchemy import create_engine
import pymysql

def db_connection():
    # modify config_map to reflect credentials needed by this program
    config_map = {
        'user':'CMSC508_USER',
        'password':'CMSC508_PASSWORD',
        'host':'CMSC508_HOST',
        'database':'ASTRONOMY_DB_NAME'
    }
    # load and store credentials
    config = {}
    for key in config_map.keys():
        config[key] = os.getenv(config_map[key])

    # build a sqlalchemy engine string
    engine_uri = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}/{config['database']}"

    # create a database connection.  THIS IS THE ACTUAL CONNECTION!
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
    cursor = cnx.cursor()

    #query database
    sql_query= f"""
    select * from observers
    """
    cursor.execute(sql_query)

    observer = {}
    observers = []
    for row in cursor.fetchall():
        observer['observer_id'] = row['observer_id']
        observer['first_name'] = row['first_name']
        observer['last_name'] = row['last_name']
        observers.append(observer)

    if observers is not None:
        return jsonify(observers)
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
