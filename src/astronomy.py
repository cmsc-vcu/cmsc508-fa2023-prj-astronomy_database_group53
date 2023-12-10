from flask import Flask, request, jsonify
from pandas.api.types import is_timedelta64_dtype
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd
import os

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
    observers = []

    for i in range(len(df['observer_id'])):
        observer = {}
        observer['observer_id'] = df['observer_id'][i]
        observer['first_name'] = df['first_name'][i]
        observer['last_name'] = df['last_name'][i]
        observers.append(observer)

    # if data exists, return it is JSON
    if observers is not None:
        return observers
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route(f'/observer/<int:id>', methods=['GET'])
def show_observer(id):
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from observers
    where observer_id={id}
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    df = df.to_dict()

    # if data exists, return it is JSON
    if df is not None:
        return jsonify({
            'observer_id' : df['observer_id'][0],
            'first_name' : df['first_name'][0],
            'last_name' : df['last_name'][0]
        })
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/events', methods=['GET'])
def show_events():
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from events
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    # format data returned
    df = df.to_dict()
    events = []
    i = 0
    while i < len(df['event_id']):
        event = {}
        id = df['event_id'][i]
        name = df['event_name'][i]
        date = df['date_occurred'][i]
        duration = df['duration'][i]
        frequency = df['frequency'][i]
        event['event_id'] = id
        event['event_name'] = name
        event['date_occurred'] = date
        event['duration'] = duration
        event['frequency'] = frequency
        events.append(event)
        i = i + 1

    # if data exists, return it is JSON
    if events is not None:
        return jsonify(events)
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/event/<int:id>', methods=['GET'])
def show_event(id):
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from events
    where event_id={id}
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    df = df.to_dict()

    # if data exists, return it is JSON
    if df is not None:
        return jsonify({
            'event_id' : df['event_id'][0], 
            'event_name' : df['event_name'][0],
            'date_occurred' : df['date_occurred'][0],
            'duration' : df['duration'][0],
            'frequency' : df['frequency'][0]
        })
    else:
        return jsonify({'message' : f'Failed to fetch observer {id}'})

@app.route('/objects', methods=['GET'])
def show_objects():
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from objects
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    # format data returned
    df = df.to_dict()
    objects = []
    i = 0
    while i < len(df['object_id']):
        object = {}
        id = df['object_id'][i]
        name = df['object_name'][i]
        type = df['type'][i]
        description = df['description'][i]
        object['observer_id'] = id
        object['name'] = name
        object['type'] = type
        object['description'] = description
        objects.append(object)
        i = i + 1

    # if data exists, return it is JSON
    if objects is not None:
        return jsonify(objects)
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/object/<int:id>', methods=['GET'])
def show_object(id):
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from objects
    where object_id={id}
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    df = df.to_dict()

    # if data exists, return it is JSON
    if df is not None:
        return jsonify({
            'object_id' : df['object_id'][0],
            'object_name' : df['object_name'][0],
            'type' : df['type'][0],
            'description' : df['description'][0]
        })
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/earth_locations', methods=['GET'])
def show_earth_locations():
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from earth_locations
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    # format data returned
    df = df.to_dict()
    locations = []
    i = 0
    while i < len(df['earth_location_id']):
        location = {}
        id = df['earth_location_id'][i]
        quad = df['quadrant'][i]
        lat = df['latitude'][i]
        long = df['longitude'][i]
        timezone = df['timezone'][i]
        time = df['local_time'][i]
        desc = df['description'][i]
        location['earth_location_id'] = id
        location['quadrant'] = quad
        location['latitude'] = lat
        location['longitude'] = long
        location['timezone'] = timezone
        location['local_time'] = time
        location['description'] = desc
        locations.append(location)
        i = i + 1

    # if data exists, return it is JSON
    if locations is not None:
        return jsonify(locations)
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/earth_location/<int:id>', methods=['GET'])
def show_earth_location(id):
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from earth_locations
    where earth_location_id={id}
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    df = df.to_dict()

    # if data exists, return it is JSON
    if df is not None:
        return jsonify({
            'earth_location_id' : df['earth_location_id'][0],
            'quadrant' : df['quadrant'][0],
            'latitude' : df['latitude'][0],
            'longitude' : df['longitude'][0],
            'timezone' : df['timezone'][0],
            'local_time' : df['local_time'][0],
            'description' : df['description'][0]
        })
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/space_locations', methods=['GET'])
def show_space_locations():
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from space_locations
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    df_notdict = df
    df = df.to_dict()

    # Convert Timedelta columns to compatible format
    for col in df_notdict.columns:
        if is_timedelta64_dtype(df_notdict[col]):
            df[col] = df_notdict[col].astype(str)

    # format data returned
    locations = []
    i = 0
    while i < len(df['space_location_id']):
        location = {}
        id = df['space_location_id'][i]
        ra = df['ra'][i]
        de = df['de'][i]
        description = df['description'][i]
        location['space_location_id'] = id
        location['ra'] = ra
        location['de'] = de
        location['description'] = description
        locations.append(location)
        i = i + 1

    # if data exists, return it is JSON
    if locations is not None:
        return jsonify(locations)
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

#TODO: creates an error: Object of type Timedelta is not JSON serializable
@app.route('/space_location/<int:id>', methods=['GET'])
def show_space_location(id):
    # db connection
    cnx = db_connection()

    #query database
    sql= f"""
    select * from space_locations
    where space_location_id={id}
    """
    try:
        df = pd.read_sql(sql,cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        df = pd.DataFrame()

    df_notdict = df
    df = df.to_dict()

    # Convert Timedelta columns to compatible format
    for col in df_notdict.columns:
        if is_timedelta64_dtype(df_notdict[col]):
            df[col] = df_notdict[col].astype(str)

    # if data exists, return it is JSON
    if df is not None:
        return jsonify({
            'space_location_id' : df['space_location_id'][0],
            'ra' : df['ra'][0],
            'de' : df['de'][0],
            'description' : df['description'][0]
        })
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

if __name__ == "__main__":
    app.run()
