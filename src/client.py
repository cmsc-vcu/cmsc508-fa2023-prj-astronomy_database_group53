import requests
from flask import Flask
import json

app = Flask(__name__)

def get_observers():
    response = requests.get('http://localhost:5000/observers')
    if response.status_code == 200:
        data = response.json()
        print("All Observers:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def get_observer(id):
    response = requests.get(f'http://localhost:5000/observer/{id}')
    if response.status_code == 200:
        data = response.json()
        print(f"Observer {id}:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def add_observer(id, first_name, last_name):
    data = {"observer_id" : id, "first_name" : first_name, "last_name" : last_name}
    response = requests.post(f'http://localhost:5000/observers/add', json=data)
    if response.status_code == 201:
        data = response.json()
        print("Observer Added:")
        print(data, indent=4)
    elif response.status_code == 400:
        data = response.json()
        print("Error Encountered:")
        print(data)
    else:
        print(f"Request failed with status code {response.status_code}")

def get_events():
    response = requests.get('http://localhost:5000/events')
    if response.status_code == 200:
        data = response.json()
        print("All Events:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def get_event(id):
    response = requests.get(f'http://localhost:5000/event/{id}')
    if response.status_code == 200:
        data = response.json()
        print(f"Event {id}:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def add_event(id, name, date, dur, frq, desc):
    data = {"event_id": id, 
            "event_name": name, 
            "date_occurred": date,
            "duration" : dur,
            "frequency" : frq,
            "description" : desc
        }
    response = requests.post('http://localhost:5000/events/add', json=data)
    if response.status_code == 201:
        data = response.json()
        print("Event Added:")
        print(json.dumps(data, indent=4))
    elif response.status_code == 400:
        data = response.json()
        print("Error Encountered:")
        print(data)
    else:
        print(f"Request failed with status code {response.status_code}")

def get_objects():
    response = requests.get('http://localhost:5000/objects')
    if response.status_code == 200:
        data = response.json()
        print("All Objects:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def get_object(id):
    response = requests.get(f'http://localhost:5000/object/{id}')
    if response.status_code == 200:
        data = response.json()
        print(f"Object {id}:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def add_object(id, name, type, desc):
    data = {"object_id": id, "object_name": name, "type": type, "description" : desc}
    response = requests.post('http://localhost:5000/objects/add', json=data)
    if response.status_code == 201:
        data = response.json()
        print("Object Added:")
        print(json.dumps(data, indent=4))
    elif response.status_code == 400:
        data = response.json()
        print("Error Encountered:")
        print(data)
    else:
        print(f"Request failed with status code {response.status_code}")

def get_earth_locations():
    response = requests.get('http://localhost:5000/earth_locations')
    if response.status_code == 200:
        data = response.json()
        print("All Earth Locations:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def get_earth_location(id):
    response = requests.get(f'http://localhost:5000/earth_location/{id}')
    if response.status_code == 200:
        data = response.json()
        print(f"Earth Location {id}:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def add_earth_location(id, quad, long, lat, zone, time, name):
    data = {
        "earth_location_id": id,
        "quadrant": quad,
        "longitude": long,
        "latitude": lat,
        "timezone": zone,
        "local_time": time,
        "location_name": name
    }
    response = requests.post('http://localhost:5000/earth_locations/add', json=data)
    if response.status_code == 201:
        data = response.json()
        print("Earth Location Added:")
        print(json.dumps(data, indent=4))
    elif response.status_code == 400:
        data = response.json()
        print("Error Encountered:")
        print(data)
    else:
        print(f"Request failed with status code {response.status_code}")

def get_space_locations():
    response = requests.get('http://localhost:5000/space_locations')
    if response.status_code == 200:
        data = response.json()
        print("All Space Locations:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def get_space_location(id):
    response = requests.get(f'http://localhost:5000/space_location/{id}')
    if response.status_code == 200:
        data = response.json()
        print(f"Space Location {id}:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Request failed with status code {response.status_code}.")

def add_space_location(id, ra, de, desc):
    data = {
        "space_location_id": id,
        "ra": ra,
        "de": de,
        "description": desc
    }
    response = requests.post('http://localhost:5000/space_locations/add', json=data)
    if response.status_code == 201:
        response_data = response.json()
        print("Space Location Added:")
        print(json.dumps(response_data, indent=4))
    elif response.status_code == 400:
        response_data = response.json()
        print("Error Encountered:")
        print(response_data)
    else:
        print(f"Request failed with status code {response.status_code}")


if __name__ == '__main__':
    get_observers()
    print()
    get_observer(19)



    
