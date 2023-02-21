drop table if exists user;
create table if not exists user (
    user_id int PRIMARY KEY auto_increment,
    user_type enum('admin', 'cashier', 'customer') not null,
    email varchar(256) not null UNIQUE,
    name varchar(256) not null,
    pw_hash varchar(256) not null
);

drop table if exists country;
create table if not exists country (
    country_id int PRIMARY KEY auto_increment,
    name varchar(32) not null UNIQUE
);

drop table if exists city;
create table if not exists city (
    city_id int PRIMARY KEY auto_increment,
    name varchar(32) not null
);

drop table if exists manufacturer;
create table if not exists manufacturer (
    manufacturer_id int PRIMARY KEY auto_increment,
    country_id int not null references country(country_id),
    name varchar(64) not null UNIQUE
);

drop table if exists vendor;
create table if not exists vendor (
    vendor_id int PRIMARY KEY auto_increment,
    cipher varchar(256) not null UNIQUE,
    company_name varchar(64) not null UNIQUE,
    city_id int not null references city(city_id),
    conclusion_date date not null,
    termination_date date
);

drop table if exists drug_group;
create table if not exists drug_group (
    drug_group_id int PRIMARY KEY auto_increment,
    name varchar(32) not null UNIQUE
);

drop table if exists drug;
create table if not exists drug (
    drug_id int PRIMARY KEY auto_increment,
    drug_group_id int not null references drug_group(drug_group_id),
    cipher varchar(256) not null UNIQUE,
    name varchar(64) not null,
    manufacturer_id int not null references manufacturer(manufacturer_id)
);

drop table if exists vendor_item;
create table if not exists vendor_item (
    item_id int primary key auto_increment,
    vendor_id int not null references vendor(vendor_id),
    drug_id int not null references drug (drug_id),
    price decimal(10, 2) not null,
    UNIQUE (vendor_id, drug_id, price)  # a vendor cannot have same drug with same price in different rows
);


drop table if exists vendor_has_item;
create table if not exists vendor_has_item (
    vendor_id int not null references vendor(vendor_id),
    item_id int not null references vendor_item(item_id),
    amount int not null,
    UNIQUE (vendor_id, item_id)  # vendor must not have one specific item in multiple rows
);

drop table if exists pharmacy_has_drug;
create table if not exists pharmacy_has_drug (
    drug_id int not null references drug(drug_id),
    price decimal(10, 2) not null,
    amount int not null,
    UNIQUE (drug_id, price)
);

drop table if exists admin_order;
create table if not exists admin_order (
    order_id int PRIMARY KEY auto_increment,
    user_id int not null references user(user_id),
    create_date date not null,
    expect_receive_date date not null,
    receive_date date,
    cost decimal(10, 2) not null default 0
);

drop table if exists admin_order_has_item;
create table if not exists admin_order_has_item (
    order_id int not null references admin_order(order_id),
    item_id int not null references vendor_item(item_id),
    amount int not null,
    UNIQUE (order_id, item_id)
);

drop table if exists admin_cart_has_item;
create table if not exists admin_cart_has_item (
    user_id int not null references user(user_id),
    item_id int not null references vendor_item(item_id),
    amount int not null
);

drop table if exists customer_order;
create table if not exists customer_order (
    order_id int PRIMARY KEY auto_increment,
    user_id int not null references user(user_id),
    create_date date not null,
    expect_receive_date date not null,
    receive_date date,
    cost decimal(10, 2) not null default 0
);

drop table if exists customer_order_has_drug;
create table if not exists customer_order_has_drug (
    order_id int not null references customer_order(order_id),
    drug_id int not null references drug(drug_id),
    price decimal(10, 2) not null,
    amount int not null,
    UNIQUE (order_id, drug_id, price)
);

drop table if exists customer_cart_has_drug;
create table if not exists customer_cart_has_drug (
    user_id int not null references user(user_id),
    drug_id int not null references drug(drug_id),
    price decimal(10, 2) not null,
    amount int not null,
    UNIQUE (user_id, drug_id, price)
);



commit;
