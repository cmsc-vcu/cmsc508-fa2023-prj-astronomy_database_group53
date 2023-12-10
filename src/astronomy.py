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
    return jsonify({
        'message' : 'Welcome to the Astronomy Database API!'
    })

@app.route('/observers', methods=['GET'])
def show_observers():
    # db connection
    cnx = db_connection()

    # get query parameters from URL
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    # query database
    sql = "select * from observers"

    # add filters based on the provided query parameters
    conditions = []
    if first_name:
        conditions.append(f" first_name = '{first_name}'")
    if last_name:
        conditions.append(f" last_name = '{last_name}'")

    # constructing the where clause
    if conditions:
        sql += " where" + " and".join(conditions)

    if sort_by:
        sql += f" order by {sort_by}"
        if order_by:
            sql += f" {order_by}"

    if per_page:
        sql += f" limit {per_page}"
        page = request.args.get('page', default=1, type=int)
        if page > 1:
            sql += f" offset {per_page * (page - 1)}"

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
        return jsonify(observers)
    else:
        return jsonify({'message' : 'Failed to fetch observers'}), 500

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
        return jsonify({'message' : f'Failed to fetch observer {id}'}), 500
    
@app.route('/observers/add', methods=['POST'])
def add_observer():
    data = request.get_json()
    if not data:
        return jsonify({'message' : 'No data provided.'}), 400
    
    observer_id = data.get('observer_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not observer_id or not first_name or not last_name:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # db connection
    cnx = db_connection()

    # Insert the new observer into the database
    try:
        sql = "insert into observers (observer_id, first_name, last_name) values (%s, %s, %s)"
        df = pd.read_sql(sql, cnx)
        return jsonify({'message': 'Observer added successfully'}), 201
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to add observer'}), 500

@app.route('/events', methods=['GET'])
def show_events():
    # db connection
    cnx = db_connection()

    # get query parameters from URL
    name = request.args.get('name')
    date = request.args.get('date')
    duration = request.args.get('duration')
    frequency = request.args.get('frequency')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    # query database
    sql = "select * from events"

    # add filters based on the provided query parameters
    conditions = []
    if name:
        conditions.append(f" event_name = '{name}'")
    if date:
        conditions.append(f" date_occurred = '{date}'")
    if duration:
        conditions.append(f" duration = '{duration}'")
    if frequency:
        conditions.append(f" frequency = '{frequency}'")

    # constructing the where clause
    if conditions:
        sql += " where" + " and".join(conditions)

    if sort_by:
        sql += f" order by {sort_by}"
        if order_by:
            sql += f" {order_by}"

    if per_page:
        sql += f" limit {per_page}"
        page = request.args.get('page', default=1, type=int)
        if page > 1:
            sql += f" offset {per_page * (page - 1)}"
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
        return jsonify({'message' : 'Failed to fetch events'}), 500

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
        return jsonify({'message' : f'Failed to fetch event {id}'}), 500

@app.route('/objects', methods=['GET'])
def show_objects():
    # db connection
    cnx = db_connection()

    # get query parameters from URL
    name = request.args.get('object_name')
    type = request.args.get('type')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    # query database
    sql = "select * from objects"
    
    # add filters based on the provided query parameters
    conditions = []
    if name:
        conditions.append(f" event_name = '{name}'")
    if type:
        conditions.append(f" type = '{type}'")

    # constructing the where clause
    if conditions:
        sql += " where" + " and".join(conditions)

    if sort_by:
        sql += f" order by {sort_by}"
        if order_by:
            sql += f" {order_by}"

    if per_page:
        sql += f" limit {per_page}"
        page = request.args.get('page', default=1, type=int)
        if page > 1:
            sql += f" offset {per_page * (page - 1)}"
    
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
        object['object_id'] = id
        object['object_name'] = name
        object['type'] = type
        object['description'] = description
        objects.append(object)
        i = i + 1

    # if data exists, return it is JSON
    if objects is not None:
        return jsonify(objects)
    else:
        return jsonify({'message' : 'Failed to fetch objects'}), 500

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
        return jsonify({'message' : f'Failed to fetch object {id}'}), 500

@app.route('/earth_locations', methods=['GET'])
def show_earth_locations():
    # db connection
    cnx = db_connection()

    # get query parameters from URL
    quad = request.args.get('quadrant')
    lat = request.args.get('latitude')
    long = request.args.get('longitude')
    timezone = request.args.get('timezone')
    time = request.args.get('local_time')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    # query database
    sql = "select * from earth_locations"

    # add filters based on the provided query parameters
    conditions = []
    if quad:
        conditions.append(f" quadrant = '{quad}'")
    if lat:
        conditions.append(f" latitude = '{lat}'")
    if long:
        conditions.append(f" longitude = '{long}'")
    if timezone:
        conditions.append(f" timezone = '{timezone}'")
    if time:
        conditions.append(f" local_time = '{time}'")

    # constructing the where clause
    if conditions:
        sql += " where" + " and".join(conditions)

    if sort_by:
        sql += f" order by {sort_by}"
        if order_by:
            sql += f" {order_by}"

    if per_page:
        sql += f" limit {per_page}"
        page = request.args.get('page', default=1, type=int)
        if page > 1:
            sql += f" offset {per_page * (page - 1)}"

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
        return jsonify({'message' : 'Failed to fetch Earth locations'}), 500

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
        return jsonify({'message' : f'Failed to fetch Earth location {id}'}), 500

@app.route('/space_locations', methods=['GET'])
def show_space_locations():
    # db connection
    cnx = db_connection()

    # get query parameters from URL
    ra = request.args.get('ra')
    de = request.args.get('de')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    # query database
    sql = "select * from space_locations"

    # add filters based on the provided query parameters
    conditions = []
    if ra:
        conditions.append(f" ra = '{ra}'")
    if de:
        conditions.append(f" de = '{de}'")

    # constructing the where clause
    if conditions:
        sql += " where" + " and".join(conditions)

    if sort_by:
        sql += f" order by {sort_by}"
        if order_by:
            sql += f" {order_by}"

    if per_page:
        sql += f" limit {per_page}"
        page = request.args.get('page', default=1, type=int)
        if page > 1:
            sql += f" offset {per_page * (page - 1)}"

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
        return jsonify({'message' : 'Failed to fetch space locations'}), 500

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
        return jsonify({'message' : f'Failed to fetch space location {id}'}), 500

if __name__ == "__main__":
    app.run()
