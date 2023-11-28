drop table if exists observers;
drop table if exists objects;
drop table if exists events;
drop table if exists earth_locations;
drop table if exists space_locations;

create table observers (
    observer_id int not null primary key,
    first_name varchar(255) not null,
    last_name varchar(255)
);

create table objects (
    object_id int not null primary key,
    object_name varchar(255) not null,
    type varchar(255),
    description varchar(4096)
);

create table events (
    event_id int not null primary key,
    event_name varchar(255),
    date_occurred date not null,
    duration float,
    frequency float
);

create table earth_locations (
    earth_location_id int not null primary key,
    quadrant varchar(2),
    latitude float not null,
    longitude float not null,
    timezone int not null,
    local_time datetime not null
);

create table space_locations (
    space_location_id int not null primary key,
    ra time not null,
    dec float not null
);