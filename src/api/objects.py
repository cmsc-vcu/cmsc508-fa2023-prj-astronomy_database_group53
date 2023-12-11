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
    
if __name__ == "__main__":
    app.run()