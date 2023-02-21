drop trigger if exists user_delete_cart on "user";
drop function if exists user_delete_cart;
create function user_delete_cart() returns trigger as $user_delete_cart$
begin
    delete from customer_cart_has_item where user_id = old.user_id;
    if old.user_type = 'admin' then
        delete from admin_cart_has_item where user_id = old.user_id;
    end if;
    return old;
end $user_delete_cart$ language plpgsql;
create trigger user_delete_cart after delete on "user"
    for each row execute function user_delete_cart();


drop trigger if exists manufacturer_delete_country on manufacturer;
drop function if exists manufacturer_delete_country;
create function manufacturer_delete_country() returns trigger as $manufacturer_delete_country$
    declare _country_n_occurrences int default 0;
begin
    select count(*) into _country_n_occurrences from manufacturer where country_id = old.country_id;
    if _country_n_occurrences = 0 then
        delete from country where country_id = old.country_id;
    end if;
    return old;
end $manufacturer_delete_country$ language plpgsql;
create trigger manufacturer_delete_country after delete on manufacturer for each row
    execute function manufacturer_delete_country();


drop trigger if exists drug_delete_drug_group on drug;
drop function if exists drug_delete_drug_group;
create function drug_delete_drug_group() returns trigger as $drug_delete_drug_group$
        declare _group_n_occurrences int default 0;
begin
    select count(*) into _group_n_occurrences from drug where drug_group_id = old.drug_group_id;
    if _group_n_occurrences = 0 then
        delete from drug_group where drug_group_id = old.drug_group_id;
    end if;
    return old;
end $drug_delete_drug_group$ language plpgsql;
create trigger drug_delete_drug_group after delete on drug for row
    execute function drug_delete_drug_group();


drop trigger if exists vendor_delete_city on vendor;
drop function if exists vendor_delete_city;
create function vendor_delete_city() returns trigger as $vendor_delete_city$
    declare _city_n_occurrences int default 0;
begin
    select count(*) into _city_n_occurrences from vendor where city_id = old.city_id;
    if _city_n_occurrences = 0 then
        delete from city where city_id = old.city_id;
    end if;
    return old;
end $vendor_delete_city$ language plpgsql;
create trigger vendor_delete_city after delete on vendor for each row
    execute function vendor_delete_city();
