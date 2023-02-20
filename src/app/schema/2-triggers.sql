drop trigger if exists user_delete_cart;
create trigger user_delete_cart after delete on user for each row
begin
    delete from customer_cart_has_drug where user_id = old.user_id;
    if old.user_type = 'admin' then
        delete from admin_cart_has_item where user_id = old.user_id;
    end if;
end;


drop trigger if exists manufacturer_delete_country;
create trigger manufacturer_delete_country after delete on manufacturer for each row
begin
    declare _country_n_occurrences int default 0;
    select count(*) into _country_n_occurrences from manufacturer where country_id = old.country_id;
    if _country_n_occurrences = 0 then
        delete from country where country_id = old.country_id;
    end if;
end;


drop trigger if exists drug_delete_drug_group;
create trigger drug_delete_drug_group after delete on drug for each row
begin
    declare _group_n_occurrences int default 0;
    select count(*) into _group_n_occurrences from drug where drug_group_id = old.drug_group_id;
    if _group_n_occurrences = 0 then
        delete from drug_group where drug_group_id = old.drug_group_id;
    end if;
end;


drop trigger if exists vendor_delete_city;
create trigger vendor_delete_city after delete on vendor for each row
begin
    declare _city_n_occurrences int default 0;
    select count(*) into _city_n_occurrences from vendor where city_id = old.city_id;
    if _city_n_occurrences = 0 then
        delete from city where city_id = old.city_id;
    end if;
end;

drop trigger if exists admin_order_increment_cost;
create trigger admin_order_increment_cost after insert on admin_order_has_item for each row
begin
    declare _item_price decimal(10, 2);
    select price into _item_price from vendor_item where item_id = new.item_id;
    update admin_order set cost = cost + _item_price * new.amount where order_id = new.order_id;
end;

drop trigger if exists admin_order_decrement_cost;
create trigger admin_order_decrement_cost after delete on admin_order_has_item for each row
begin
    declare _item_price decimal(10, 2);
    select price into _item_price from vendor_item where item_id = old.item_id;
    update admin_order set cost = cost - _item_price * old.amount where order_id = old.order_id;
end;


drop trigger if exists admin_order_update_cost;
create trigger admin_order_update_cost after update on admin_order_has_item for each row
begin
    declare _item_price decimal(10, 2);
    select price into _item_price from vendor_item where item_id = new.item_id;
    update admin_order set cost = cost + (new.amount - old.amount) * _item_price where order_id = old.order_id;
end;


drop trigger if exists customer_order_increment_cost;
create trigger customer_order_increment_cost after insert on customer_order_has_drug for each row
begin
    update customer_order set cost = cost + new.price * new.amount where order_id = new.order_id;
end;

drop trigger if exists customer_order_decrement_cost;
create trigger customer_order_decrement_cost after delete on customer_order_has_drug for each row
begin
    update customer_order set cost = cost - old.price * old.amount where order_id = old.order_id;
end;

drop trigger if exists customer_order_update_cost;
create trigger customer_order_update_cost after update on customer_order_has_drug for each row
begin
    update customer_order set cost = cost + (new.amount - old.amount) * new.price where order_id = old.order_id;
end;


drop trigger if exists delete_vendor_item_from_cart;
create trigger delete_vendor_item_from_cart after delete on vendor_has_item for each row
begin
    delete from admin_cart_has_item where item_id = old.item_id;
end;

drop trigger if exists delete_pharmacy_item_from_cart;
create trigger delete_pharmacy_item_from_cart after delete on pharmacy_has_drug for each row
begin
    delete from customer_cart_has_drug where drug_id = old.drug_id and price = old.price;
end;

drop trigger if exists delete_pharmacy_item_from_storefront;
create trigger delete_pharmacy_item_from_storefront after update on pharmacy_has_drug for each row
begin
    if new.amount = 0 then
        delete from pharmacy_has_drug where drug_id = new.drug_id and price = new.price;
    end if;
end;

commit;