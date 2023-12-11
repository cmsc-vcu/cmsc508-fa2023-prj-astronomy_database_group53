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

if __name__ == "__main__":
    app.run()