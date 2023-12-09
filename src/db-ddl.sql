SET AUTOCOMMIT=1;

SET FOREIGN_KEY_CHECKS=0;
drop table if exists observers;
drop table if exists objects;
drop table if exists events;
drop table if exists earth_locations;
drop table if exists space_locations;
drop table if exists object_event;
drop table if exists object_location;
drop table if exists object_space_location;
drop table if exists object_object;
drop table if exists event_location;
drop table if exists observer_event;
drop table if exists observer_object;

SET FOREIGN_KEY_CHECKS=1;

create table observers (
    observer_id int not null primary key,
    first_name varchar(255) not null,
    last_name varchar(255)
);

INSERT INTO observers (observer_id, first_name, last_name) VALUES
    (1, 'Henrietta', 'Leavitt'),
    (2, 'Hypatia', 'Alexandria'),
    (3, 'Uma', 'Manicka'),
    (4, 'Celeste', 'Olmstead'),
    (5, 'John', 'Leonard'),
    (6, 'Astrid', 'Vega'),
    (7, 'Galileo', 'Galilei'),
    (8, 'Maria', 'Mitchell'),
    (9, 'Isaac', 'Newton'),
    (10, 'Catherine', 'Herschel'),
    (11, 'Edmond', 'Halley'),
    (12, 'Caroline', 'Herschel'),
    (13, 'Tycho', 'Brahe'),
    (14, 'Edwin', 'Hubble'),
    (15, 'Annie', 'Jump Cannon');


create table objects (
    object_id int not null primary key,
    object_name varchar(255) not null,
    type varchar(255),
    description varchar(4096)
);

INSERT INTO objects (object_id, object_name, type, description) VALUES
    (1, 'andromeda galaxy', 'galaxy', 'Spiral galaxy visible to the naked eye.'),
    (2, 'orion nebula', 'nebula', 'Emission nebula in the Orion constellation.'),
    (3, 'jupiter', 'planet', 'The largest planet in our solar system.'),
    (4, 'pleiades', 'star cluster', 'Open star cluster in Taurus constellation.'),
    (5, 'sun', 'star', 'our solar systems star'),
    (6, 'horsehead nebula', 'nebula', 'Dark nebula in the constellation Orion.'),
    (7, 'andromeda ii', 'galaxy', 'Dwarf galaxy in the Andromeda Galaxy subgroup.'),
    (8, 'saturn', 'planet', 'Sixth planet from the Sun, known for its prominent rings.'),
    (9, 'm42', 'nebula', 'The Orion Nebula, a diffuse nebula situated in the Milky Way.'),
    (10, 'crab nebula', 'nebula', 'Supernova remnant in the constellation Taurus.'),
    (11, 'Ganymede', 'moon', 'Jupiters largest moon'),
    (12, 'm13', 'star cluster', 'Globular cluster in the Hercules constellation.'),
    (13, 'mars', 'planet', 'Fourth planet from the Sun, often referred to as the Red Planet.'),
    (14, 'bee-hive cluster', 'star cluster', 'Open cluster in the constellation Cancer.'),
    (15, 'andromeda iii', 'galaxy', 'Dwarf galaxy in the Andromeda Galaxy subgroup.')
    (16, 'moon', 'moon', 'Earths moon');

create table events (
    event_id int not null primary key,
    event_name varchar(255),
    date_occurred date not null,
    duration float,
    frequency float
);

INSERT INTO events (event_id, event_name, date_occurred, duration, frequency) VALUES
    (1, 'total lunar eclipse', '2023-10-20', 2.0, 1.0),
    (2, 'meteor shower', '2023-11-15', 6.0, 2.0),
    (3, 'comet sighting', '2024-03-05', 1.0, 3.0),
    (4, 'supernova observation', '2024-06-12', 4.0, 4.0),
    (5, 'planetary conjunction', '2024-08-30', 0.5, 5.0),
    (6, 'total solar eclipse', '2023-12-01', 2.0, 1.0),
    (7, 'super blue moon', '2023-12-14', 3.5, 2.5),
    (8, 'hypernova observation', '2024-04-20', 1.5, 3.0),
    (9, 'bright comet sighting', '2024-07-25', 2.0, 4.0);
    


create table earth_locations (
    earth_location_id int not null primary key,
    quadrant varchar(2),
    latitude float not null,
    longitude float not null,
    timezone varchar(255) not null,
    local_time datetime not null,
    description varchar(4096)

);

INSERT INTO earth_locations (earth_location_id, quadrant, latitude, longitude, timezone, local_time, description) VALUES
    (1, 'NW', 40.7128, -74.0060, 'UTC-4', '2023-10-15 16:00:00', 'New York City, USA'),
    (2, 'SW', 34.0522, -118.2437, 'UTC-7', '2023-10-15 13:00:00', 'Los Angeles, USA'),
    (3, 'NE', 51.5074, -0.1278, 'UTC+0', '2023-10-15 20:00:00', 'London, UK'),
    (4, 'SE', 33.4484, -112.0740, 'UTC-7', '2023-10-15 13:00:00', 'Phoenix, USA'),
    (5, 'NW', 41.8781, -87.6298, 'UTC-5', '2023-10-15 15:00:00', 'Chicago, USA'),
    (6, 'SE', -23.5505, -46.6333, 'UTC-3', '2023-10-15 14:00:00', 'São Paulo, Brazil'),
    (7, 'NE', 55.7558, 37.6176, 'UTC+3', '2023-10-15 21:00:00', 'Moscow, Russia'),
    (8, 'SW', -33.8688, 151.2093, 'UTC+11', '2023-10-16 01:00:00', 'Sydney, Australia'),
    (9, 'NW', 48.8566, 2.3522, 'UTC+1', '2023-10-15 17:00:00', 'Paris, France');
    
create table space_locations (
    space_location_id int not null primary key,
    ra time not null,
    de varchar(255) not null
);

INSERT INTO space_locations (space_location_id, ra, de) VALUES
    (1, '00:42:44', '+41° 16'' 09"'),
    (2, '05:35:17', '-05° 23'' 28"'),
    (3, '20:22:38', '-18° 40'' 48"'),
    (4, '03:47:24', '+24° 07'' 00"'),
    (5, '05:41:02', '-02° 27'' 30"'),
    (6, '08:00:12', '+15° 45'' 36"'),  -- Example 1
    (7, '12:30:55', '-10° 12'' 15"'), -- Example 2
    (8, '18:55:20', '-32° 18'' 02"'), -- Example 3
    (9, '22:15:33', '+02° 50'' 20"'), -- Example 4
    (10, '02:10:08', '-45° 30'' 55"'); -- Example 5

CREATE TABLE object_event (
    id int auto_increment,
    object_id INT NOT NULL,
    event_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (object_id) REFERENCES objects(object_id) on delete cascade,
    FOREIGN KEY (event_id) REFERENCES events(event_id) on delete cascade,
    unique(event_id, object_id)
);

CREATE TABLE event_location (
    id int auto_increment,
    event_id INT NOT NULL,
    location_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (event_id) REFERENCES events(event_id) on delete cascade,
    FOREIGN KEY (location_id) REFERENCES earth_locations(earth_location_id) on delete cascade,
    unique(event_id, location_id)

);

CREATE TABLE object_location (
    id int auto_increment,
    object_id INT NOT NULL,
    location_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (object_id) REFERENCES objects(object_id) on delete cascade,
    FOREIGN KEY (location_id) REFERENCES earth_locations(earth_location_id) on delete cascade,
    unique(object_id, location_id)

);

CREATE TABLE object_space_location (
    id int auto_increment,
    object_id INT NOT NULL,
    space_location_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (object_id) REFERENCES objects(object_id) on delete cascade,
    FOREIGN KEY (space_location_id) REFERENCES space_locations(space_location_id) on delete cascade,
    unique(object_id, space_location_id)
);

CREATE TABLE observer_event (
    id int auto_increment,
    observer_id INT NOT NULL,
    event_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (observer_id) REFERENCES observers(observer_id) on delete cascade,
    FOREIGN KEY (event_id) REFERENCES events(event_id) on delete cascade,
    unique(observer_id, event_id)
);

CREATE TABLE observer_object (
    id INT auto_increment,
    observer_id INT NOT NULL,
    object_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (observer_id) REFERENCES observers(observer_id) on delete cascade,
    FOREIGN KEY (object_id) REFERENCES objects(object_id) on delete cascade,
    unique(observer_id, object_id)
);

CREATE TABLE object_object (
    id INT auto_increment,
    object1_id INT NOT NULL,
    object2_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (object1_id) REFERENCES objects(object_id) on delete cascade,
    FOREIGN KEY (object2_id) REFERENCES objects(object_id) on delete cascade,
    unique(object1_id, object2_id)
);


INSERT INTO object_event (object_id, event_id)
VALUES
    (5, 6), -- sol and total solar eclipse
    (11 , 1), -- total lunar eclipse
    (8, 5), -- Saturn and Planetary Conjunction
    (3, 5), -- jupiter and Planetary Conjunction
    (4, 2), -- Star Cluster and Meteor Shower
    (16, 7), -- super blue moon
    (5, 1); -- supernova

INSERT INTO event_location (event_id, location_id)
VALUES
    (1, 1), -- lunar eclipse in Boston
    (2, 2), -- Meteor Shower in San Francisco
    (3, 3), -- comet Sighting Miami
    (4, 4), -- supernova Observation Los Angeles
    (5, 5); -- planetary conj philly
    (7, 9); -- super blue moon paris

INSERT INTO object_location (object_id, location_id)
VALUES
    (1, 4),  -- Andromeda Galaxy in LA
    (2, 2),  -- Orion Nebula in San Francisco
    (5, 3),  -- Jupiter in London
    (8, 3),  -- Saturn in London
    (5, 5),  -- Horsehead Nebula in Chicago
    (16, 9) -- moon paris

INSERT INTO object_space_location (object_id, space_location_id)
SELECT o.object_id, sl.space_location_id
FROM objects o, space_locations sl;

INSERT INTO observer_event (observer_id, event_id)
SELECT obs.observer_id, e.event_id
FROM observers obs, events e;

INSERT INTO observer_object (observer_id, object_id)
SELECT obs.observer_id, o.object_id
FROM observers obs, objects o;

INSERT INTO object_object (object1_id, object2_id)
SELECT o1.object_id, o2.object_id
FROM objects o1, objects o2
WHERE o1.object_id < o2.object_id;
