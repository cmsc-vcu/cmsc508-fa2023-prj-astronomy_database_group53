from pandas.api.types import is_timedelta64_dtype
from sqlalchemy import create_engine, text
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
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
        
def authorization():
    authorized = False
    if "Authorization" in request.headers:
        token = request.headers['Authorization']
        if token == 'Bearer super-secret':
            authorized = True
    return authorized


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'


# observer endpoints
@app.route('/')
def index():
    return jsonify({
        'message' : 'Welcome to the Astronomy Database API!'
    })

@app.route('/observers', methods=['GET'])
def show_observers():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401

    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    sql = "select * from observers"
    conditions = []

    if first_name:
        conditions.append(f"first_name = '{first_name}'")
    if last_name:
        conditions.append(f"last_name = '{last_name}'")

    if conditions:
        sql += " where " + " and ".join(conditions)

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
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    if data is not None:
        observers = []
        for row in data.fetchall():
            observer = {
                'observer_id': row[0],
                'first_name': row[1],
                'last_name': row[2]
            }
            observers.append(observer)
        return jsonify(observers)
    else:
        return jsonify({'message': 'Failed to find observers.'}), 404

@app.route(f'/observer/<int:id>', methods=['GET'])
def show_observer(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    #db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    sql = f"select * from observers where observer_id = {id}"

    try:
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    data = data.fetchone()
    if data is not None:
        observer_details = {
            'observer_id': data[0],
            'first_name': data[1],
            'last_name': data[2]
        }
        return jsonify({'observer_details': observer_details})
    else:
        return jsonify({'message': f'Failed to find observer {id}'}), 404

@app.route('/observers/add', methods=['POST'])
def add_observer():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    observer_id = data.get('observer_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select observer_id from observers where observer_id = {observer_id}"
        observer = pd.read_sql(sql_check, cnx)

        if observer.empty:
            if not observer_id or not first_name or not last_name:
                return jsonify({'message': 'Missing required fields.'}), 400

            df = pd.DataFrame({
                'observer_id': [observer_id],
                'first_name': [first_name],
                'last_name': [last_name]
            })

            df.to_sql('observers', con=cnx, if_exists='append', index=False)
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': 'Observer added successfully.', 'observer_details': {
                'observer_id': observer_id,
                'first_name': first_name,
                'last_name': last_name
            }}), 200
        else:
            cnx_conn.close()
            return jsonify({"message": f"Observer of id {observer_id} already exists."}), 400

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to add observer.', 'error': message}), 500

@app.route('/observers/remove/<int:id>', methods=['DELETE'])
def remove_observer(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select observer_id from observers where observer_id = {id}"
        observer = pd.read_sql(sql_check, cnx)

        if not observer.empty:
            sql_delete = f"delete from observers where observer_id = {id}"
            cnx_conn.execute(text(sql_delete))
            cnx_conn.commit()
            cnx_conn.close()
            
            return jsonify({'message': f"Successfully removed observer {id}."}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Observer {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to remove observer.', 'error': message}), 500

@app.route('/observers/edit/<int:id>', methods=['POST'])
def update_observer(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    # db connection
    cnx = db_connection()
    cnx_conn = cnx.connect()

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    attributes = data.get('attribute')
    values = data.get('value')
    if not attributes or not values or len(attributes) != len(values):
        return jsonify({'message': 'Invalid attributes or values.'}), 400

    try:
        sql_check = f"select observer_id from observers where observer_id = {id}"
        observer = pd.read_sql(sql_check, cnx)

        if not observer.empty:
            sql_update = "update observers set "
            set_values = []
            for att, val in zip(attributes, values):
                if att.lower() == 'observer_id':
                    return jsonify({"message": 'Primary keys cannot be changed.'}), 400
                else:
                    set_values.append(f"{att} = '{val}'")

            sql_update += ", ".join(set_values)
            sql_update += f" where observer_id = {id}"

            cnx_conn.execute(text(sql_update))
            cnx_conn.commit()

            info = pd.read_sql(f"select * from observers where observer_id = {id}", cnx)
            cnx_conn.close()
            updated = info.to_dict(orient='records')[0]

            return jsonify({'message': 'Observer updated successfully.', 'observer_details': updated}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Observer {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to update observer.', 'error': message}), 500


# event endpoints
@app.route('/events', methods=['GET'])
def show_events():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    event_name = request.args.get('event_name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')
    frequency = request.args.get('frequency')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    sql = "select * from events"
    conditions = []

    if event_name:
        conditions.append(f"event_name = '{event_name}'")

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            conditions.append(f"date_occurred between '{start_date}' and '{end_date}'")
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if min_duration and max_duration:
        conditions.append(f"duration between {min_duration} and {max_duration}")

    if frequency:
        conditions.append(f"frequency = '{frequency}'")

    if conditions:
        sql += " where " + " and ".join(conditions)

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
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    if data is not None:
        events = []
        for row in data.fetchall():
            event = {
                'event_id': row[0],
                'event_name': row[1],
                'date_occurred': row[2],
                'duration': row[3],
                'frequency': row[4]
            }
            events.append(event)
        return jsonify(events)
    else:
        return jsonify({'message': 'Failed to find events.'}), 404

@app.route(f'/event/<int:id>', methods=['GET'])
def show_event(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    sql = f"select * from events where event_id = {id}"

    try:
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    data = data.fetchone()
    if data is not None:
        event_details = {
            'event_id': data[0],
            'event_name': data[1],
            'date_occurred': data[2],
            'duration': data[3],
            'frequency': data[4]
        }
        return jsonify({'event_details': event_details})
    else:
        return jsonify({'message': f'Failed to find event {id}'}), 404

@app.route('/events/add', methods=['POST'])
def add_event():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    event_id = data.get('event_id')
    event_name = data.get('event_name')
    date_occurred = data.get('date_occurred')
    duration = data.get('duration')
    frequency = data.get('frequency')

    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select event_id from events where event_id = {event_id}"
        event = pd.read_sql(sql_check, cnx)

        if event.empty:
            if not event_id or not event_name or not date_occurred:
                return jsonify({'message': 'Missing required fields.'}), 400

            sql_add = f"insert into events (event_id, event_name, date_occurred, duration, frequency) values " \
                      f"({event_id}, '{event_name}', '{date_occurred}', {duration}, '{frequency}')"

            cnx_conn.execute(text(sql_add))
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': 'Event added successfully.', 'event_details': {
                'event_id': event_id,
                'event_name': event_name,
                'date_occurred': date_occurred,
                'duration': duration,
                'frequency': frequency
            }}), 200
        else:
            cnx_conn.close()
            return jsonify({"message": f"Event of id {event_id} already exists."}), 400

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to add event.', 'error': message}), 500

@app.route('/events/remove/<int:id>', methods=['DELETE'])
def remove_event(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select event_id from events where event_id = {id}"
        event = pd.read_sql(sql_check, cnx)

        if not event.empty:
            sql_delete = f"delete from events where event_id = {id}"
            cnx_conn.execute(text(sql_delete))
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': f"Successfully removed event {id}."}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Event {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to remove event.', 'error': message}), 500

@app.route('/events/edit/<int:id>', methods=['POST'])
def update_event(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    attributes = data.get('attribute')
    values = data.get('value')
    if not attributes or not values or len(attributes) != len(values):
        return jsonify({'message': 'Invalid attributes or values.'}), 400

    try:
        sql_check = f"select event_id from events where event_id = {id}"
        event = pd.read_sql(sql_check, cnx)

        if not event.empty:
            sql_update = "update events set "
            set_values = []
            for att, val in zip(attributes, values):
                if att.lower() == 'event_id':
                    return jsonify({"message": 'Primary keys cannot be changed.'}), 400
                else:
                    set_values.append(f"{att} = '{val}'")

            sql_update += ", ".join(set_values)
            sql_update += f" where event_id = {id}"

            cnx_conn.execute(text(sql_update))
            cnx_conn.commit()

            info = pd.read_sql(f"select * from events where event_id = {id}", cnx)
            cnx_conn.close()
            updated = info.to_dict(orient='records')[0]

            return jsonify({'message': 'Event updated successfully.', 'event_details': updated}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Event {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to update event.', 'error': message}), 500


# object endpoints
@app.route('/objects', methods=['GET'])
def show_objects():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    object_name = request.args.get('object_name')
    object_type = request.args.get('type')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    sql = "select * from objects"
    conditions = []

    if object_name:
        conditions.append(f"object_name = '{object_name}'")

    if object_type:
        conditions.append(f"type = '{object_type}'")

    if conditions:
        sql += " where " + " and ".join(conditions)

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
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    if data is not None:
        objects = []
        for row in data.fetchall():
            obj = {
                'object_id': row[0],
                'object_name': row[1],
                'type': row[2],
                'description': row[3]
            }
            objects.append(obj)
        return jsonify(objects)
    else:
        return jsonify({'message': 'Failed to find objects.'}), 404

@app.route(f'/object/<int:id>', methods=['GET'])
def show_object(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    sql = f"select * from objects where object_id = {id}"

    try:
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    data = data.fetchone()
    if data is not None:
        object_details = {
            'object_id': data[0],
            'object_name': data[1],
            'type': data[2],
            'description': data[3]
        }
        return jsonify({'object_details': object_details})
    else:
        return jsonify({'message': f'Failed to find object {id}'}), 404

@app.route('/objects/add', methods=['POST'])
def add_object():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    object_id = data.get('object_id')
    object_name = data.get('object_name')
    object_type = data.get('type')
    description = data.get('description')

    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select object_id from objects where object_id = {object_id}"
        obj = pd.read_sql(sql_check, cnx)

        if obj.empty:
            if not object_id or not object_name or not object_type:
                return jsonify({'message': 'Missing required fields.'}), 400

            df = pd.DataFrame({
                'object_id': [object_id],
                'object_name': [object_name],
                'type': [object_type],
                'description': [description]
            })

            df.to_sql('objects', con=cnx, if_exists='append', index=False)
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': 'Object added successfully.', 'object_details': {
                'object_id': object_id,
                'object_name': object_name,
                'type': object_type,
                'description': description
            }}), 200
        else:
            cnx_conn.close()
            return jsonify({"message": f"Object of id {object_id} already exists."}), 400

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to add object.', 'error': message}), 500

@app.route('/objects/remove/<int:id>', methods=['DELETE'])
def remove_object(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select object_id from objects where object_id = {id}"
        obj = pd.read_sql(sql_check, cnx)

        if not obj.empty:
            sql_delete = f"delete from objects where object_id = {id}"
            cnx_conn.execute(text(sql_delete))
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': f"Successfully removed object {id}."}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Object {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to remove object.', 'error': message}), 500

@app.route('/objects/edit/<int:id>', methods=['POST'])
def update_object(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    attributes = data.get('attribute')
    values = data.get('value')
    if not attributes or not values or len(attributes) != len(values):
        return jsonify({'message': 'Invalid attributes or values.'}), 400

    try:
        sql_check = f"select object_id from objects where object_id = {id}"
        obj = pd.read_sql(sql_check, cnx)

        if not obj.empty:
            sql_update = "update objects set "
            set_values = []
            for att, val in zip(attributes, values):
                if att.lower() == 'object_id':
                    return jsonify({"message": 'Primary keys cannot be changed.'}), 400
                else:
                    set_values.append(f"{att} = '{val}'")

            sql_update += ", ".join(set_values)
            sql_update += f" where object_id = {id}"

            cnx_conn.execute(text(sql_update))
            cnx_conn.commit()

            info = pd.read_sql(f"select * from objects where object_id = {id}", cnx)
            cnx_conn.close()
            updated = info.to_dict(orient='records')[0]

            return jsonify({'message': 'Object updated successfully.', 'object_details': updated}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Object {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to update object.', 'error': message}), 500


# earth_locations endpoints
@app.route('/earth_locations', methods=['GET'])
def show_earth_locations():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    quadrant = request.args.get('quadrant')
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    timezone = request.args.get('timezone')
    location_name = request.args.get('location_name')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    sql = "select * from earth_locations"
    conditions = []

    if quadrant:
        conditions.append(f"quadrant = '{quadrant}'")
    if longitude:
        conditions.append(f"longitude = {longitude}")
    if latitude:
        conditions.append(f"latitude = {latitude}")
    if timezone:
        conditions.append(f"timezone = '{timezone}'")
    if location_name:
        conditions.append(f"location_name = '{location_name}'")

    if conditions:
        sql += " where " + " and ".join(conditions)

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
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    if data is not None:
        earth_locations = []
        for row in data.fetchall():
            earth_location = {
                'earth_location_id': row[0],
                'quadrant': row[1],
                'longitude': row[2],
                'latitude': row[3],
                'timezone': row[4],
                'local_time': str(row[5]),
                'location_name': row[6]
            }
            earth_locations.append(earth_location)
        return jsonify(earth_locations)
    else:
        return jsonify({'message': 'Failed to find earth locations.'}), 404

@app.route(f'/earth_location/<int:id>', methods=['GET'])
def show_earth_location(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    sql = f"select * from earth_locations where earth_location_id = {id}"

    try:
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    data = data.fetchone()
    if data is not None:
        earth_location_details = {
            'earth_location_id': data[0],
            'quadrant': data[1],
            'longitude': data[2],
            'latitude': data[3],
            'timezone': data[4],
            'local_time': str(data[5]),
            'location_name': data[6]
        }
        return jsonify({'earth_location_details': earth_location_details})
    else:
        return jsonify({'message': f'Failed to find earth location {id}'}), 404

@app.route('/earth_locations/add', methods=['POST'])
def add_earth_location():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    earth_location_id = data.get('earth_location_id')
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    timezone = data.get('timezone')
    quadrant = data.get('quadrant')
    location_name = data.get('location_name')
    local_time = data.get('local_time')
    local_time = str(local_time)

    # Check for required fields
    if not all([earth_location_id, longitude, latitude, timezone, local_time]):
        return jsonify({'message': 'Missing required fields.'}), 400

    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select earth_location_id from earth_locations where earth_location_id = {earth_location_id}"
        earth_loc = pd.read_sql(sql_check, cnx)

        if earth_loc.empty:
            df = pd.DataFrame({
                'earth_location_id': [earth_location_id],
                'quadrant' : [quadrant],
                'longitude': [longitude],
                'latitude': [latitude],
                'timezone': [timezone],
                'local_time': [local_time],
                'location_name' : [location_name]
            })

            df.to_sql('earth_locations', con=cnx, if_exists='append', index=False)
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': 'Earth location added successfully.', 'earth_location_details': {
                'earth_location_id': earth_location_id,
                'quadrant' : quadrant,
                'longitude': longitude,
                'latitude': latitude,
                'timezone': timezone,
                'local_time': local_time,
                'location_name' : location_name
            }}), 200
        else:
            cnx_conn.close()
            return jsonify({"message": f"Earth location of id {earth_location_id} already exists."}), 400

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to add earth location.', 'error': message}), 500

@app.route('/earth_locations/remove/<int:id>', methods=['DELETE'])
def remove_earth_location(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select earth_location_id from earth_locations where earth_location_id = {id}"
        earth_loc = pd.read_sql(sql_check, cnx)

        if not earth_loc.empty:
            sql_delete = f"delete from earth_locations where earth_location_id = {id}"
            cnx_conn.execute(text(sql_delete))
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': f"Successfully removed earth location {id}."}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Earth location {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to remove earth location.', 'error': message}), 500

@app.route('/earth_locations/edit/<int:id>', methods=['POST'])
def update_earth_location(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    attributes = data.get('attribute')
    values = data.get('value')

    # Check for required fields
    if not attributes or not values or len(attributes) != len(values):
        return jsonify({'message': 'Invalid attributes or values.'}), 400

    try:
        sql_check = f"select earth_location_id from earth_locations where earth_location_id = {id}"
        obj = pd.read_sql(sql_check, cnx)

        if not obj.empty:
            sql_update = "update earth_locations set "
            set_values = []
            for att, val in zip(attributes, values):
                if att.lower() == 'earth_location_id':
                    return jsonify({"message": 'Primary keys cannot be changed.'}), 400
                else:
                    set_values.append(f"{att} = '{val}'")

            sql_update += ", ".join(set_values)
            sql_update += f" where earth_location_id = {id}"

            cnx_conn.execute(text(sql_update))
            cnx_conn.commit()

            info = pd.read_sql(f"select * from earth_locations where earth_location_id = {id}", cnx)
            cnx_conn.close()
            updated = info.to_dict(orient='records')[0]
            updated['local_time'] = str(updated['local_time'])

            return jsonify({'message': 'Earth location updated successfully.', 'location_details': updated}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Earth location {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to update earth location.', 'error': message}), 500


# space location endpoints
@app.route('/space_locations', methods=['GET'])
def show_space_locations():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    ra = request.args.get('ra')
    de = request.args.get('de')
    description = request.args.get('description')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')
    per_page = request.args.get('per_page')

    sql = "select * from space_locations"
    conditions = []

    if ra:
        conditions.append(f"ra = '{ra}'")
    if de:
        conditions.append(f"de = '{de}'")
    if description:
        conditions.append(f"description = '{description}'")

    if conditions:
        sql += " where " + " and ".join(conditions)

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
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    if data is not None:
        space_locations = []
        for row in data.fetchall():
            space_location = {
                'space_location_id': row[0],
                'ra': str(row[1]),
                'de': row[2],
                'description': row[3]
            }
            space_locations.append(space_location)
        return jsonify(space_locations)
    else:
        return jsonify({'message': 'Failed to find space locations.'}), 404

@app.route(f'/space_location/<int:id>', methods=['GET'])
def show_space_location(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    sql = f"select * from space_locations where space_location_id = {id}"

    try:
        data = cnx_conn.execute(text(sql))
        cnx_conn.commit()
        cnx_conn.close()
    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to execute query', 'error': message}), 500

    data = data.fetchall()
    if data is not None:
        for row in data:
            space_location_details = {
                'space_location_id': row[0],
                'ra': str(row[1]),
                'de': row[2],
                'description': row[3]
            } 
        return jsonify({'space_location_details': space_location_details})
    else:
        cnx_conn.close()
        return jsonify({'message': f'Failed to find space location {id}'}), 404

@app.route('/space_locations/add', methods=['POST'])
def add_space_location():
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    space_location_id = data.get('space_location_id')
    ra = data.get('ra')
    de = data.get('de')
    description = data.get('description')

    # Check for required fields
    if not all([space_location_id, ra, de]):
        return jsonify({'message': 'Missing required fields.'}), 400

    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select space_location_id from space_locations where space_location_id = {space_location_id}"
        space_loc = pd.read_sql(sql_check, cnx)

        if space_loc.empty:
            df = pd.DataFrame({
                'space_location_id': [space_location_id],
                'ra': [ra],
                'de': [de],
                'description': [description]
            })

            df.to_sql('space_locations', con=cnx, if_exists='append', index=False)
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': 'Space location added successfully.', 'space_location_details': {
                'space_location_id': space_location_id,
                'ra': str(ra),
                'de': de,
                'description': description
            }}), 200
        else:
            cnx_conn.close()
            return jsonify({"message": f"Space location of id {space_location_id} already exists."}), 400

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to add space location.', 'error': message}), 500

@app.route('/space_locations/remove/<int:id>', methods=['DELETE'])
def remove_space_location(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    try:
        sql_check = f"select space_location_id from space_locations where space_location_id = {id}"
        space_loc = pd.read_sql(sql_check, cnx)

        if not space_loc.empty:
            sql_delete = f"delete from space_locations where space_location_id = {id}"
            cnx_conn.execute(text(sql_delete))
            cnx_conn.commit()
            cnx_conn.close()

            return jsonify({'message': f"Successfully removed space location {id}."}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Space location {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to remove space location.', 'error': message}), 500

@app.route('/space_locations/edit/<int:id>', methods=['POST'])
def update_space_location(id):
    if not authorization():
        return jsonify({'message' : 'Access denied, must provide token.'}), 401
    
    cnx = db_connection()
    cnx_conn = cnx.connect()

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    attributes = data.get('attribute')
    values = data.get('value')

    # Check for required fields
    if not attributes or not values or len(attributes) != len(values):
        return jsonify({'message': 'Invalid attributes or values.'}), 400

    try:
        sql_check = f"select space_location_id from space_locations where space_location_id = {id}"
        obj = pd.read_sql(sql_check, cnx)

        if not obj.empty:
            sql_update = "update space_locations set "
            set_values = []
            for att, val in zip(attributes, values):
                if att.lower() == 'space_location_id':
                    return jsonify({"message": 'Primary keys cannot be changed.'}), 400
                else:
                    set_values.append(f"{att} = '{val}'")

            sql_update += ", ".join(set_values)
            sql_update += f" where space_location_id = {id}"

            cnx_conn.execute(text(sql_update))
            cnx_conn.commit()

            info = pd.read_sql(f"select * from space_locations where space_location_id = {id}", cnx)
            cnx_conn.close()
            updated = info.to_dict(orient='records')[0]
            updated['ra'] = str(updated['ra'])

            return jsonify({'message': 'Space location updated successfully.', 'location_details': updated}), 200
        else:
            cnx_conn.close()
            return jsonify({'message': f'Space location {id} not found.'}), 404

    except Exception as e:
        message = str(e)
        return jsonify({'message': 'Failed to update space location.', 'error': message}), 500


if __name__ == "__main__":
    app.run()
