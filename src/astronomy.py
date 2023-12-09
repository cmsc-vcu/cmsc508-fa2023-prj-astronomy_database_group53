from flask import Flask, request, jsonify
import os
import pandas as pd
from sqlalchemy import create_engine

#TODO: figure out this connection and querying the database
def db_connection():
    # modify config_map to reflect credentials needed by this program
    config_map = {
        'user':'23FA_olmsteadca',
        'password':'Shout4_olmsteadca_GOME',
        'host':'cmsc508.com',
        'database':'23FA_groups_group53'
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
cnx = db_connection()

@app.route('/')
def index():
    return "welcome"

@app.route('/observers', methods=['GET'])
def show_observers():
    # get any queries
    limit = request.args.get('limit')
    sort = request.args.getlist('sort')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')

    if limit is None:
        limit = 10
    
    if sort is None:
        sort = ["id", "asc"]

    if first_name is None and last_name is None:
        #query database
        pass
    
    if last_name is None:
        #query database
        pass
    
    if first_name is None:
        #query database
        pass

@app.route('/events', methods=['GET'])
def show_events():
    pass

@app.route('/objects', methods=['GET'])
def show_objects():
    pass

if __name__ == "__main__":
    app.run()
