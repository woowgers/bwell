drop trigger if exists user_delete_cart;
create trigger user_delete_cart after delete on user for each row
begin
    delete from customer_cart_has_item where user_id = old.user_id;
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
