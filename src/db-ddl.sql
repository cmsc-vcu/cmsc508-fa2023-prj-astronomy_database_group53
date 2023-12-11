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
    (9, 'crab nebula', 'nebula', 'Supernova remnant in the constellation Taurus.'),
    (10, 'Ganymede', 'moon', 'Jupiters largest moon'),
    (11, 'moon', 'moon', 'Earths moon');

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
    local_time time not null,
    location_name varchar(4096)

);

INSERT INTO earth_locations (earth_location_id, quadrant, latitude, longitude, timezone, local_time, location_name) VALUES
    (1, 'NW', 40.7128, -74.0060, 'UTC-4', '16:00:00', 'New York City, USA'),
    (2, 'SW', 34.0522, -118.2437, 'UTC-7', '13:00:00', 'Los Angeles, USA'),
    (3, 'NE', 51.5074, -0.1278, 'UTC+0', '20:00:00', 'London, UK'),
    (4, 'SE', 33.4484, -112.0740, 'UTC-7', '13:00:00', 'Phoenix, USA'),
    (5, 'NW', 41.8781, -87.6298, 'UTC-5', '15:00:00', 'Chicago, USA'),
    (6, 'SE', -23.5505, -46.6333, 'UTC-3', '14:00:00', 'Sao Paulo, Brazil'),
    (7, 'NE', 55.7558, 37.6176, 'UTC+3', '21:00:00', 'Moscow, Russia'),
    (8, 'SW', -33.8688, 151.2093, 'UTC+11', '01:00:00', 'Sydney, Australia'),
    (9, 'NW', 48.8566, 2.3522, 'UTC+1', '17:00:00', 'Paris, France');
    
create table space_locations (
    space_location_id int not null primary key,
    ra time not null,
    de varchar(255) not null,
    description varchar(255)
);

INSERT INTO space_locations (space_location_id, ra, de, description) VALUES
    (1, '00:42:44', '+41° 16'' 09"', 'Constellation Andromeda'),
    (2, '05:35:17', '-05° 23'' 28"', 'Constellation Taurus'),
    (3, '20:22:38', '-18° 40'' 48"', 'Center of the Milky Way'),
    (4, '05:41:02', '-02° 27'' 30"', 'Constellation Orion'),
    (5, '12:30:55', '-10° 12'' 15"', 'Constellation Virgo'),
    (6, '22:15:33', '+02° 50'' 20"', 'Constellation Aquarius'),
    (7, '21:04:10', '-15° 36'' 22"', 'Constellation Capricornus');

CREATE TABLE object_event (
    id int auto_increment,
    object_id INT NOT NULL,
    event_id INT NOT NULL,
    date_occurred date NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (object_id) REFERENCES objects(object_id) on delete cascade,
    FOREIGN KEY (event_id) REFERENCES events(event_id) on delete cascade,
    unique(event_id, object_id)
);

CREATE TABLE event_location (
    id int auto_increment,
    event_id INT NOT NULL,
    location_id INT NOT NULL,
    date_occurred date NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (event_id) REFERENCES events(event_id) on delete cascade,
    FOREIGN KEY (location_id) REFERENCES earth_locations(earth_location_id) on delete cascade,
    unique(event_id, location_id)

);

CREATE TABLE object_location (
    id int auto_increment,
    object_id INT NOT NULL,
    location_id INT NOT NULL,
    date_occurred date NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (object_id) REFERENCES objects(object_id) on delete cascade,
    FOREIGN KEY (location_id) REFERENCES earth_locations(earth_location_id) on delete cascade,
    unique(object_id, location_id)

);

CREATE TABLE object_space_location (
    id int auto_increment,
    object_id INT NOT NULL,
    space_location_id INT NOT NULL,
    date_occurred date NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (object_id) REFERENCES objects(object_id) on delete cascade,
    FOREIGN KEY (space_location_id) REFERENCES space_locations(space_location_id) on delete cascade,
    unique(object_id, space_location_id)
);

CREATE TABLE observer_event (
    id int auto_increment,
    observer_id INT NOT NULL,
    event_id INT NOT NULL,
    date_occurred date NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (observer_id) REFERENCES observers(observer_id) on delete cascade,
    FOREIGN KEY (event_id) REFERENCES events(event_id) on delete cascade,
    unique(observer_id, event_id)
);

CREATE TABLE observer_object (
    id INT auto_increment,
    observer_id INT NOT NULL,
    object_id INT NOT NULL,
    date_occurred date NOT NULL,
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


INSERT INTO object_event (object_id, event_id, date_occurred)
VALUES
    (5, 6, '2023-12-01'), -- sol and total solar eclipse
    (10, 1, '2023-10-20'), -- total lunar eclipse
    (8, 5, '2024-08-30'), -- Saturn and Planetary Conjunction
    (3, 5, '2024-08-30'), -- jupiter and Planetary Conjunction
    (4, 2, '2023-11-15'), -- Star Cluster and Meteor Shower
    (11, 7, '2023-12-14'), -- super blue moon
    (5, 1, '2024-06-12'); -- supernova

INSERT INTO event_location (event_id, location_id, date_occurred)
VALUES
    (1, 1, '2023-10-20'), -- lunar eclipse in Boston
    (2, 2, '2023-11-15'), -- Meteor Shower in San Francisco
    (3, 3, '2024-03-05'), -- comet Sighting Miami
    (4, 4, '2024-06-12'), -- supernova Observation Los Angeles
    (5, 5, '2024-08-30'), -- planetary conj philly
    (3, 5, '2025-10-20'),
    (7, 9, '2024-07-25'); -- super blue moon paris


INSERT INTO object_location (object_id, location_id, date_occurred)
VALUES
    (1, 5,'2023-10-20' ),
    (2, 1, '2023-11-15'),
    (3, 6, '2024-03-05'),
    (4, 4, '2024-03-05'),
    (5, 2, '2024-08-30'),
    (9, 2, '2024-09-30'),
    (1, 2, '2024-08-30'),
    (6, 3, '2023-12-01'),
    (7, 9, '2023-12-14'),
    (8, 8, '2024-04-20'),
    (9, 7, '2024-03-05');

INSERT INTO object_space_location (object_id, space_location_id, date_occurred)
VALUES
    (1, 1, '2023-10-20'),  -- total lunar eclipse - Andromeda Galaxy - Constellation Andromeda
    (2, 4, '2023-11-15'),  -- meteor shower - Orion is in Orion
    (3, 6, '2024-03-05'),  -- comet sighting - Jupiter - Center of the Milky Way - Constellation Aquarius
    (4, 2, '2024-06-12'),  -- supernova observation - Pleiades Star Cluster - Taurus
    (5, 3, '2024-08-30'),  -- planetary conjunction - Sun - Center
    (6, 4, '2023-12-01'),  -- total solar eclipse - Horse Nebula is in Orion
    (7, 1, '2023-12-14'),  -- super blue moon - Andromeda 2 - Andromeda
    (8, 7, '2024-04-20'),  -- hypernova observation - Saturn - Constellation Capricornus
    (9, 2, '2024-07-25'),  -- bright comet sighting - Crab Nebula - Taurus
    (10, 6, '2022-09-23'),  -- ganymede
    (11, 5, '2023-12-09');  -- our moon - Virgo (as of 12/9/2023)

INSERT INTO observer_event (observer_id, event_id, date_occurred)
VALUES
    (1, 1, '2023-10-20'),
    (2, 2, '2023-11-15'),
    (3, 3, '2024-03-05'),
    (4, 4, '2024-06-12'),
    (5, 5, '2024-08-30'),
    (6, 6, '2023-12-01'),
    (7, 7, '2023-12-14'),
    (8, 8, '2024-04-20'),
    (9, 9, '2024-07-25'),
    (10, 5, '2024-08-30'),
    (11, 1, '2023-10-20'),
    (12, 3, '2024-03-05'),
    (13, 7, '2023-12-14'),
    (14, 8, '2024-04-20'),
    (15, 9, '2024-07-25');


INSERT INTO observer_object (observer_id, object_id, date_occurred)
VALUES
    (1, 3, '2024-03-05'),
    (2, 4, '2024-06-12'),
    (3, 2, '2023-11-15'),
    (4, 1, '2023-10-20'),
    (5, 10, '2020-10-24'),
    (6, 9, '2024-07-25'),
    (7, 7, '2023-12-14'),
    (8, 6, '2023-12-01'),
    (9, 8, '2024-04-20'),
    (10, 1, '2023-10-20'),
    (11, 4, '2024-06-12'),
    (12, 5, '2024-08-30'),
    (13, 2, '2023-11-15'),
    (14, 3, '2024-03-05'),
    (15, 11, '2022-01-10');

INSERT INTO object_object (object1_id, object2_id)
VALUES
  (3, 8);
  
