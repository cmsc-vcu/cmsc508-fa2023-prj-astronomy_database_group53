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
    
if __name__ == "__main__":
    app.run()