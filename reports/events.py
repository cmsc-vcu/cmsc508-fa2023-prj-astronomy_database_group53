import requests
from flask import Flask
import json

app = Flask(__name__)
header = {'Authorization' :'Bearer super-secret'}

# events endpoints
def get_events():
    response = requests.get('http://localhost:5000/events', headers=header)
    data = response.json()
    if response.status_code == 200:
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")
        if data: 
            print(data)

def get_event(id):
    response = requests.get(f'http://localhost:5000/event/{id}',headers=header)
    data = response.json()
    if response.status_code == 200:
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")
        if data: 
            print(data)

def add_event(id, name, date, dur, frq):
    new_data = {
        "event_id" : id,
        "event_name" : name,
        "date_occurred" : date,
        "duration" : dur,
        "frequency" : frq
    }
    response = requests.post('http://localhost:5000/events/add', json=new_data, headers=header)
    data = response.json()
    if response.status_code == 200:
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}")
        if data: 
            print(data)

def remove_event(id):
    rm_data = {"event_id": id}
    response = requests.delete(f'http://localhost:5000/events/remove/{id}', json=rm_data, headers=header)
    data = response.json()
    if response.status_code == 200:
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}")
        if data: 
            print(data)

def update_event(id, attribute, value):
    new_data = {
        "attribute": attribute,
        "value": value
    }
    response = requests.post(f'http://localhost:5000/events/edit/{id}', json=new_data, headers=header)
    data = response.json()
    if response.status_code == 200:
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}")
        if data: 
            print(data)


# print output
if __name__ == '__main__':
    get_events()
    print()
    add_event(16, name='Party', date='2023-12-31', dur='.33', frq='2')
    print()
    get_event(16)
    print()
    update_event(16, ['event_name'], ['Birthday Party'])
    print()
    remove_event(16)
    print()