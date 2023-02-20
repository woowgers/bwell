drop procedure if exists get_country_create_if_not_exists;
create procedure get_country_create_if_not_exists(
    inout _country_id int,
    inout _name varchar(256)
)
begin
    start transaction;
    select country_id into _country_id from country where name = _name;
    if _country_id is null then
        insert into country (name) value (_name);
        select last_insert_id() into _country_id;
    end if;
    commit;
end;


drop procedure if exists create_admin_order;
create procedure create_admin_order(
    inout _order_id int,
    inout _user_id int,
    inout _create_date date,
    inout _expect_receive_date date,
    inout _receive_date date,
    inout _cost decimal
)
begin
    insert into admin_order (user_id, create_date, expect_receive_date) value (_user_id, _create_date, _expect_receive_date);
    select last_insert_id() into _order_id;
    select receive_date, cost into _receive_date, _cost from admin_order where order_id = _order_id;
end;


drop procedure if exists create_customer_order;
create procedure create_customer_order(
    inout _order_id int,
    inout _user_id int,
    inout _create_date date,
    inout _expect_receive_date date,
    inout _receive_date date,
    inout _cost decimal
)
begin
    insert into customer_order (user_id, create_date, expect_receive_date) value (_user_id, _create_date, _expect_receive_date);
    select last_insert_id() into _order_id;
    select receive_date, cost into _receive_date, _cost from customer_order where order_id = _order_id;
end;


drop procedure if exists move_item_from_admin_cart_to_order;
create procedure move_item_from_admin_cart_to_order(
    in _user_id int,
    in _order_id int,
    in _item_id int,
    in _amount int
)
begin
    declare _amount_vendor_has int;
    select amount into _amount_vendor_has from vendor_has_item where item_id = _item_id;
    start transaction;
    insert into admin_order_has_item (order_id, item_id, amount) value (_order_id, _item_id, _amount);
    delete from admin_cart_has_item where user_id = _user_id and item_id = _item_id;
    if _amount < _amount_vendor_has then
        update vendor_has_item set amount = amount - _amount where item_id = _item_id;
    elseif _amount = _amount_vendor_has then
        delete from vendor_has_item where item_id = _item_id;
    else
        rollback;
        signal sqlstate '23000' set message_text = 'Vendor does not have enough of given item on storefront.';
    end if;
    commit;
end;


drop procedure if exists move_drug_from_customer_cart_to_order;
create procedure move_drug_from_customer_cart_to_order(
    in _user_id int,
    in _order_id int,
    in _drug_id int,
    in _price decimal(10, 2),
    in _amount int
)
begin
    declare _amount_pharmacy_has int;
    select amount into _amount_pharmacy_has from pharmacy_has_drug where drug_id = _drug_id and price = _price;
    start transaction;
    insert into customer_order_has_drug (order_id, drug_id, price, amount) value (_order_id, _drug_id, _price, _amount);
    delete from customer_cart_has_drug where user_id = _user_id and drug_id = _drug_id;
    if _amount < _amount_pharmacy_has then
        update pharmacy_has_drug set amount = amount - _amount where drug_id = _drug_id and price = _price;
    elseif _amount = _amount_pharmacy_has then
        delete from pharmacy_has_drug where drug_id and price = _price;
    else
        rollback;
        signal sqlstate '23000' set message_text = 'Pharmacy does not have enough of given drug.';
    end if;
    commit;
end;


drop procedure if exists receive_admin_order;
create procedure receive_admin_order(
    in _order_id int,
    in _receive_date date
)
begin
    declare _item_price decimal(10, 2);
    declare _extra_charge decimal(10, 2) default 0.15;
    declare _item_id, _drug_id, _amount int;
    declare done boolean default false;
    declare cur cursor for select item_id, amount from admin_order_has_item where order_id = _order_id;
    declare continue handler for not found set done = true;
    open cur;
    `read_items`: loop
        fetch cur into _item_id, _amount;
        if done then leave `read_items`; end if;
        select drug_id, price into _drug_id, _item_price from vendor_item where item_id = _item_id;
        select (1 + _extra_charge) * _item_price into _item_price;
        insert into pharmacy_has_drug (drug_id, price, amount) value (_drug_id, _item_price, _amount)
            on duplicate key update amount = amount + _amount;
    end loop;
    close cur;
    update admin_order set receive_date = _receive_date where order_id = _order_id;
end;

drop procedure if exists receive_customer_order;
create procedure receive_customer_order(
    in _order_id int,
    in _receive_date date
)
begin
    declare _price decimal(10, 2);
    declare _item_id, _drug_id, _amount int;
    declare done boolean default false;
    declare cur cursor for select drug_id, price, amount from customer_order_has_drug where order_id = _order_id;
    declare continue handler for not found set done = true;
    open cur;
    `read_items`: loop
        fetch cur into _item_id, _price, _amount;
        if done then leave `read_items`; end if;
        update pharmacy_has_drug set amount = amount - _amount where drug_id = _drug_id and price = _price;
    end loop;
    close cur;
    update customer_order set receive_date = _receive_date where order_id = _order_id;
end;

commit;
