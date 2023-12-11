from flask import Flask, request, jsonify
from pandas.api.types import is_timedelta64_dtype
from sqlalchemy import create_engine, text
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


# observer endpoints
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
        return jsonify({'message' : 'Failed to find observers.'}), 404

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
        return jsonify({'message' : f'Failed to find observer {id}'}), 404
    
@app.route('/observers/add', methods=['POST'])
def add_observer():
    data = request.get_json()

    if not data:
        return jsonify({'message' : 'No data provided.'}), 400
    
    observer_id = data.get('observer_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    df = pd.DataFrame({
        'observer_id' : [observer_id],
        'first_name' : [first_name],
        'last_name' : [last_name]
    })
    
    if not observer_id or not first_name or not last_name:
        return jsonify({'message': 'Missing required fields.'}), 400
    
    # db connection
    cnx = db_connection()

    # Insert the new observer into the database
    try:
        df.to_sql('observers', con=cnx, if_exists='append', index=False)
        return jsonify({'message': 'Observer added successfully.'}), 201
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to add observer.'}), 500

@app.route('/observers/remove/<int:id>', methods=['DELETE'])
def remove_observer(id):
    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        # check if observer exists
        sql = f"select observer_id from observers where observer_id={id}"
        observer = pd.read_sql(sql, cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to check observer existence.'}), 500
    
    if not observer.empty:
        try:
            # remove observer
            sql = f"delete from observers where observer_id={id}"
            cnx_conn.execute(text(sql))
            cnx_conn.commit()
            cnx_conn.close()
            return jsonify({'message' : f"Successfully removed observer {id}"}), 200
        except Exception as e:
            message = str(e)
            print(f"An error occurred during second try:\n\n{message}\n\nIgnoring and moving on.")
            return jsonify({'message': 'Failed to remove observer.'}), 500
    else:
        return jsonify({'message': f'Observer {id} not found.'}), 404


# event endpoints
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
        return jsonify({'message' : 'Failed to find events'}), 404

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
        return jsonify({'message' : f'Failed to find event {id}'}), 404

@app.route('/events/add', methods=['POST'])
def add_event():
    data = request.get_json()

    if not data:
        return jsonify({'message' : 'No data provided.'}), 400
    
    event_id = data.get('event_id')
    event_name = data.get('event_name')
    date_occurred = data.get('date_occurred')
    duration = data.get('duration')
    frequency = data.get('duration')

    df = pd.DataFrame[{
        'event_id' : [event_id],
        'event_name' : [event_name],
        'date_occurred' : [date_occurred],
        'duration' : [duration],
        'frequency' : [frequency]
    }]

    if not event_id or not event_name or not date_occurred:
        return jsonify({'message': 'Missing required fields.'}), 400
    
    # db connection
    cnx = db_connection()

    # Insert the new event into the database
    try:
        df.to_sql('events', con=cnx, if_exists='append', index=False)
        return jsonify({'message': 'Event added successfully.'}), 201
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to add event.'}), 500

@app.route('/events/remove/<int:id>', methods=['DELETE'])
def remove_event(id):
    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        # Check if the event exists
        sql = f"select event_id from events where event_id={id}"
        event = pd.read_sql(sql, cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to check event existence.'}), 500
    
    if not event.empty:
        try:
            # Remove event
            sql = f"delete from events where event_id={id}"
            cnx_conn.execute(text(sql))
            cnx_conn.commit()
            cnx_conn.close()
            return jsonify({'message': f'Successfully removed event {id}'}), 200
        except Exception as e:
            message = str(e)
            print(f"An error occurred during second try:\n\n{message}\n\nIgnoring and moving on.")
            return jsonify({'message': 'Failed to remove event.'}), 500
    else:
        return jsonify({'message': f'Event {id} not found.'}), 404


# object endpoints
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
    if df is not None:
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
        return jsonify({'message' : 'Failed to find objects.'}), 404

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
        return jsonify({'message' : f'Failed to find object {id}'}), 404

@app.route('/objects/add', methods=['POST'])
def add_object():
    data = request.get_json()

    if not data:
        return jsonify({'message' : 'No data provided.'}), 400
    
    object_id = data.get('object_id')
    object_name = data.get('object_name')
    type = data.get('type')
    desc = data.get('description')

    df = pd.DataFrame({
        'object_id' : [object_id],
        'object_name' : [object_name],
        'type' : [type],
        'description' : [desc]
    })
    
    if not object_id or not object_name:
        return jsonify({'message': 'Missing required fields.'}), 400
    
    # db connection
    cnx = db_connection()

    # Insert the new object into the database
    try:
        df.to_sql('objects', con=cnx, if_exists='append', index=False)
        return jsonify({'message': 'Object added successfully.'}), 201
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to add object.'}), 500

@app.route('/objects/remove/<int:id>', methods=['DELETE'])
def remove_object(id):
    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        # Check if the object exists
        sql = f"select object_id from objects where object_id={id}"
        obj = pd.read_sql(sql, cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to check object existence.'}), 500
    
    if not obj.empty:
        try:
            # Remove object
            sql = f"delete from objects where object_id={id}"
            cnx_conn.execute(text(sql))
            cnx_conn.commit()
            cnx_conn.close()
            return jsonify({'message': f'Successfully removed object {id}'}), 200
        except Exception as e:
            message = str(e)
            print(f"An error occurred during second try:\n\n{message}\n\nIgnoring and moving on.")
            return jsonify({'message': 'Failed to remove object.'}), 500
    else:
        return jsonify({'message': f'Object {id} not found.'}), 404


# earth_location endpoints
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
    if df is not None:
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
        return jsonify({'message' : 'Failed to find Earth locations.'}), 404

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
        return jsonify({'message' : f'Failed to find Earth location {id}.'}), 404

@app.route('/earth_locations/add', methods=['POST'])
def add_earth_location():
    data = request.get_json()

    if not data:
        return jsonify({'message' : 'No data provided.'}), 400
    
    id = data.get('earth_location_id')
    quad = data.get('quadrant')
    long = data.get('longitude')
    lat = data.get('latitude')
    zone = data.get('timezone')
    time = data.get('local_time')
    name = data.get('location_name')

    df = pd.DataFrame({
        'earth_location_id' : [id],
        'quadrant' : [quad],
        'longitude' : [long],
        'latitude' : [lat],
        'timezone' : [zone],
        'local_time' : [time],
        'location_name' : [name]
    })
    
    if not id or not long or not lat or not zone or not time:
        return jsonify({'message': 'Missing required fields.'}), 400
    
    # db connection
    cnx = db_connection()

    # Insert the new earth location into the database
    try:
        df.to_sql('earth_locations', con=cnx, if_exists='append', index=False)
        return jsonify({'message': 'Earth location added successfully.'}), 201
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to add Earth location.'}), 500

@app.route('/earth_locations/remove/<int:id>', methods=['DELETE'])
def remove_earth_location(id):
    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        # Check if the earth location exists
        sql = f"select earth_location_id from earth_locations where earth_location_id={id}"
        earth_loc = pd.read_sql(sql, cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to check earth location existence.'}), 500
    
    if not earth_loc.empty:
        try:
            # Remove earth location
            sql = f"delete from earth_locations where earth_location_id={id}"
            cnx_conn.execute(text(sql))
            cnx_conn.commit()
            cnx_conn.close()
            return jsonify({'message': f'Successfully removed earth location {id}'}), 200
        except Exception as e:
            message = str(e)
            print(f"An error occurred during second try:\n\n{message}\n\nIgnoring and moving on.")
            return jsonify({'message': 'Failed to remove earth location.'}), 500
    else:
        return jsonify({'message': f'Earth location {id} not found.'}), 404


# space location endpoints
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
    if df is not None:
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
        return jsonify({'message' : 'Failed to find space locations.'}), 404

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
        return jsonify({'message' : f'Failed to find space location {id}.'}), 404

@app.route('/space_locations/add', methods=['POST'])
def add_space_location():
    data = request.get_json()

    if not data:
        return jsonify({'message' : 'No data provided.'}), 400
    
    id = data.get('space_location_id')
    ra = data.get('ra')
    de = data.get('de')
    desc = data.get('description')

    df = pd.DataFrame({
        'space_location_id' : [id],
        'ra' : [ra],
        'de'  : [de],
        'description' : [desc]
    })
    
    if not id or not ra or not de:
        return jsonify({'message': 'Missing required fields.'}), 400
    
    # db connection
    cnx = db_connection()

    # Insert the new space location into the database
    try:
        df.to_sql('space_locations', con=cnx, if_exists='append', index=False)
        return jsonify({'message': 'Space location added successfully.'}), 201
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to add space location.'}), 500

@app.route('/space_locations/remove/<int:id>', methods=['DELETE'])
def remove_space_location(id):
    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        # Check if the space location exists
        sql = f"select space_location_id from space_locations where space_location_id={id}"
        space_loc = pd.read_sql(sql, cnx)
    except Exception as e:
        message = str(e)
        print(f"An error occurred:\n\n{message}\n\nIgnoring and moving on.")
        return jsonify({'message': 'Failed to check space location existence.'}), 500
    
    if not space_loc.empty:
        try:
            # Remove space location
            sql = f"delete from space_locations where space_location_id={id}"
            cnx_conn.execute(text(sql))
            cnx_conn.commit()
            cnx_conn.close()
            return jsonify({'message': f'Successfully removed space location {id}'}), 200
        except Exception as e:
            message = str(e)
            print(f"An error occurred during second try:\n\n{message}\n\nIgnoring and moving on.")
            return jsonify({'message': 'Failed to remove space location.'}), 500
    else:
        return jsonify({'message': f'Space location {id} not found.'}), 404


if __name__ == "__main__":
    app.run()
