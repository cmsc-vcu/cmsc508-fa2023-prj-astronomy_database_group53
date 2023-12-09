from flask import Flask, request, jsonify
import os
import pandas as pd
from sqlalchemy import create_engine
import pymysql

def db_connection():
    cnx = None
    try:
        cnx = pymysql.connect(
            host='cmsc508.com',
            database='23FA_groups_group53',
            user='23FA_olmsteadca',
            password='Shout4_olmsteadca_GOME',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(e)
    return cnx
        
app = Flask(__name__)

@app.route('/')
def index():
    return "welcome"

@app.route('/observers', methods=['GET'])
def show_observers():
    # db connection
    cnx = db_connection()
    cursor = cnx.cursor()

    #query database
    sql_query= f"""
    select * from observers
    """
    cursor.execute(sql_query)

    observer = {}
    observers = []
    for row in cursor.fetchall():
        observer['observer_id'] = row['observer_id']
        observer['first_name'] = row['first_name']
        observer['last_name'] = row['last_name']
        observers.append(observer)

    if observers is not None:
        return jsonify(observers)
    else:
        return jsonify({'message' : 'Failed to fetch observers'})

@app.route('/events', methods=['GET'])
def show_events():
    pass

@app.route('/objects', methods=['GET'])
def show_objects():
    pass

if __name__ == "__main__":
    app.run()
