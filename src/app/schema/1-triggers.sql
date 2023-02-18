drop trigger if exists user_delete_cart__trigger on "user";
drop procedure if exists user_delete_cart;
create procedure user_delete_cart
LANGUAGE SQL
BEGIN ATOMIC
    delete from customer_cart_has_item where user_id = old.user_id;
    if old.user_type = 'admin' then
        delete from admin_cart_has_item where user_id = old.user_id;
    end if;
end;
create trigger user_delete_cart_trigger after delete on "user" for each row execute user_delete_cart


drop trigger if exists manufacturer_delete_country__trigger on manufacturer;
drop procedure if exists manufacturer_delete_country;
create procedure manufacturer_delete_country()
LANGUAGE SQL
BEGIN ATOMIC
    declare _country_n_occurrences int default 0;
    select count(*) into _country_n_occurrences from manufacturer where country_id = old.country_id;
    if _country_n_occurrences = 0 then
        delete from country where country_id = old.country_id;
    end if;
end;
create trigger manufacturer_delete_country__trigger after delete on manufacturer for each row execute manufacturer_delete_country;


drop trigger if exists drug_delete_drug_group__trigger on drug;
drop procedure if exists drug_delete_drug;
create procedure drug_delete_drug()
LANGUAGE SQL
begin atomic
    declare _group_n_occurrences int default 0;
    select count(*) into _group_n_occurrences from drug where drug_group_id = old.drug_group_id;
    if _group_n_occurrences = 0 then
        delete from drug_group where drug_group_id = old.drug_group_id;
    end if;
end;
create trigger drug_delete_drug_group after delete on drug for each row execute drug_delete_drug_group;


drop trigger if exists vendor_delete_city__trigger on vendor;
drop procedure if exists vendor_delete_city;
create procedure if exists vendor_delete_city()
LANGUAGE SQL
BEGIN ATOMIC
    declare _city_n_occurrences int default 0;
    select count(*) into _city_n_occurrences from vendor where city_id = old.city_id;
    if _city_n_occurrences = 0 then
        delete from city where city_id = old.city_id;
    end if;
end;
create trigger vendor_delete_city__trigger after delete on vendor for each row execute vendor_delete_city;
