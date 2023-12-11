from pandas.api.types import is_timedelta64_dtype
from sqlalchemy import create_engine, text
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'

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
    
if __name__ == "__main__":
    app.run()