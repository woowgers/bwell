
drop table if exists pharmacy_order_has_item;
drop table if exists customer_order_has_item;
drop table if exists pharmacy_order;
drop table if exists customer_order;

drop table if exists customer_cart_has_item;
drop table if exists admin_cart_has_item;
drop table if exists vendor_has_item;
drop table if exists pharmacy_has_item;
drop table if exists vendor_item;
drop table if exists pharmacy_item;

drop table if exists user;

drop table if exists drug;
drop table if exists drug_group;

drop table if exists vendor;
drop table if exists manufacturer;
drop table if exists country;
drop table if exists city;


create table user (
    user_id int PRIMARY KEY auto_increment,
    user_type enum('admin', 'cashier', 'customer') not null,
    email varchar(256) not null UNIQUE,
    name varchar(256) not null,
    pw_hash varchar(256) not null
);

create table country (
    country_id int PRIMARY KEY auto_increment,
    name varchar(256) not null UNIQUE
);

create table city (
    city_id int PRIMARY KEY auto_increment,
    name varchar(256) not null
);

create table manufacturer (
    manufacturer_id int PRIMARY KEY auto_increment,
    country_id int not null references country(country_id),
    name varchar(256) not null UNIQUE
);

create table vendor (
    vendor_id int PRIMARY KEY auto_increment,
    cipher varchar(256) not null UNIQUE,
    company_name varchar(256) not null UNIQUE,
    city_id int not null references city(city_id),
    conclusion_date date not null,
    termination_date date
);

create table drug_group (
    drug_group_id int PRIMARY KEY auto_increment,
    name varchar(256) not null UNIQUE
);

create table drug (
    drug_id int PRIMARY KEY auto_increment,
    drug_group_id int not null references drug_group(drug_group_id),
    cipher varchar(256) not null UNIQUE,
    name varchar(256) not null,
    manufacturer_id int not null references manufacturer(manufacturer_id)
);

create table vendor_item (
    item_id int primary key auto_increment,
    vendor_id int not null references vendor(vendor_id),
    drug_id int not null references drug (drug_id),
    price decimal(10,2) not null,
    UNIQUE (vendor_id, drug_id, price)  # a vendor cannot have same drug with same price in different rows
);

create table pharmacy_item (
    item_id int primary key auto_increment,
    drug_id int not null references drug(drug_id),
    price decimal(10,2) not null,
    UNIQUE (drug_id, price)  # items comprising of same drug and same price must not exist
);

create table vendor_has_item (
    vendor_id int not null references vendor(vendor_id),
    item_id int not null references vendor_item(item_id),
    amount int not null,
    UNIQUE (vendor_id, item_id)  # vendor must not have one specific item in multiple rows
);

create table pharmacy_has_item (
    item_id int not null references pharmacy_item(item_id),
    amount int not null,
    UNIQUE (item_id)  # pharmacy must not have one specific item in multiple rows
);

create table pharmacy_order (
    order_id int PRIMARY KEY auto_increment,
    vendor_id int not null references vendor(vendor_id),
    create_date date not null,
    expect_receive_date date not null,
    receive_date date,
    cost decimal(10, 2) not null default 0
);

create table pharmacy_order_has_item (
    order_id int not null references pharmacy_order(order_id),
    drug_id int not null references drug(drug_id),
    price decimal (10, 2) not null,
    amount int not null,
    UNIQUE (order_id, drug_id, price)
);

create table customer_order (
    order_id int PRIMARY KEY auto_increment,
    user_id int not null references user(user_id),
    create_date date not null,
    expect_receive_date date not null,
    receive_date date,
    cost decimal(10, 2) not null default 0
);

create table customer_order_has_item (
    order_id int not null references customer_order(order_id),
    item_id int not null references pharmacy_item(item_id),
    amount int not null,
    UNIQUE (order_id, item_id)
);

create table customer_cart_has_item (
    user_id int not null references user(user_id),
    item_id int not null references pharmacy_item(item_id),
    amount int not null
);

create table admin_cart_has_item (
    user_id int not null references user(user_id),
    item_id int not null references vendor_item(item_id),
    amount int not null
);
