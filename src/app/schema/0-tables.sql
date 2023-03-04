
drop table if exists pharmacy_order_has_item, customer_order_has_item;
drop table if exists pharmacy_order, customer_order;

drop table if exists customer_cart_has_item, admin_cart_has_item, vendor_has_item, pharmacy_has_item;
drop table if exists vendor_item, pharmacy_item;

drop table if exists "user";

drop table if exists drug, drug_group;
drop table if exists vendor, manufacturer, country, city;

drop type if exists UserType;
drop domain if exists Naming, Email, PasswordHash;

create type UserType as enum ('admin', 'cashier', 'customer');
create domain Naming varchar(32);
create domain Email varchar(256);
create domain PasswordHash varchar(256);


create table if not exists "user" (
    user_id serial primary key,
    user_type UserType not null,
    email Email not null UNIQUE,
    name Naming not null,
    pw_hash PasswordHash not null
);

create table if not exists country (
    country_id serial primary key,
    name Naming not null UNIQUE
);

create table if not exists city (
    city_id serial primary key,
    name Naming not null
);

create table if not exists manufacturer (
    manufacturer_id serial primary key,
    country_id int not null references country(country_id),
    name Naming not null UNIQUE
);

create table if not exists vendor (
    vendor_id uuid primary key,
    company_name Naming not null UNIQUE,
    city_id int not null references city(city_id),
    conclusion_date date not null,
    termination_date date
);

create table if not exists drug_group (
    drug_group_id serial primary key,
    name Naming not null UNIQUE
);

create table if not exists drug (
    drug_id uuid primary key,
    drug_group_id int not null references drug_group(drug_group_id),
    name Naming not null,
    manufacturer_id int not null references manufacturer(manufacturer_id)
);

create table if not exists vendor_item (
    item_id serial primary key,
    vendor_id uuid not null references vendor(vendor_id),
    drug_id uuid not null references drug (drug_id),
    price money not null,
    UNIQUE (vendor_id, drug_id, price)  -- a vendor cannot have same drug with same price in different rows
);

create table if not exists pharmacy_item (
    item_id serial primary key,
    drug_id uuid not null references drug(drug_id),
    price money not null,
    UNIQUE (drug_id, price)  -- items comprising of same drug and same price must not exist
);

create table if not exists vendor_has_item (
    vendor_id uuid not null references vendor(vendor_id),
    item_id int not null references vendor_item(item_id),
    amount int not null,
    UNIQUE (vendor_id, item_id)  -- vendor must not have one specific item in multiple rows
);

create table if not exists pharmacy_has_item (
    item_id int not null references pharmacy_item(item_id),
    amount int not null,
    UNIQUE (item_id)  -- pharmacy must not have one specific item in multiple rows
);

create table if not exists pharmacy_order (
    order_id serial primary key,
    vendor_id uuid not null references vendor(vendor_id),
    create_date date not null,
    expect_receive_date date not null,
    receive_date date,
    cost money not null default 0
);

create table if not exists pharmacy_order_has_item (
    order_id int not null references pharmacy_order(order_id),
    item_id int not null references vendor_item(item_id),
    amount int not null,
    UNIQUE (order_id, item_id)
);

create table if not exists customer_order (
    order_id serial primary key,
    user_id int not null references "user"(user_id),
    create_date date not null,
    expect_receive_date date not null,
    receive_date date,
    cost money not null default 0
);

create table if not exists customer_order_has_item (
    order_id int not null references customer_order(order_id),
    item_id int not null references pharmacy_item(item_id),
    amount int not null,
    UNIQUE (order_id, item_id)
);

create table if not exists customer_cart_has_item (
    user_id int not null references "user"(user_id),
    item_id int not null references pharmacy_item(item_id),
    amount int not null,
    UNIQUE (user_id, item_id)
);

create table if not exists admin_cart_has_item (
    user_id int not null references "user"(user_id),
    item_id int not null references vendor_item(item_id),
    amount int not null,
    UNIQUE (user_id, item_id)
);
