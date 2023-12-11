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