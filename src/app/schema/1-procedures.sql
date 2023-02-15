
drop procedure if exists _show_procedures;
create procedure _show_procedures()
select routine_name, routine_type from information_schema.routines where routine_schema = database();

drop procedure if exists _drop_procedures;
create procedure _drop_procedures()
begin
    declare procedure_name varchar(256);
    declare done boolean default false;
    declare cur cursor for select routine_name from information_schema.routines where routine_schema = database();
    declare continue handler for not found set done = true;

    open cur;
    `read_procedures`: loop
        fetch cur into procedure_name;
        if done then leave `read_procedures`; end if;
        if substr(procedure_name, 1, 1) != '_' then
            prepare drop_procedure_statement from concat('drop procedure ', procedure_name);
            execute drop_procedure_statement;
            deallocate prepare drop_procedure_statement;
        end if;
    end loop;
    close cur;
end;


drop procedure if exists country_get_id;
create procedure country_get_id(
    out _country_id int,
    in _name varchar(256)
)
begin
    select country_id into _country_id from country where name = _name;
    if _country_id is null then
        insert into country (name) value (_name);
        select last_insert_id() into _country_id;
    end if;
end;


drop procedure if exists city_get_id;
create procedure city_get_id(
    out _city_id int,
    in _city_name varchar(256)
)
begin
    select city_id into _city_id from city where city.name = _city_name;
    if _city_id is null then
        insert into city (name) value (_city_name);
        select last_insert_id() into _city_id;
    end if;
end;


drop procedure if exists drug_group_get_id;
create procedure drug_group_get_id(
    out _group_id int,
    in _name varchar(256)
)
begin
    select drug_group_id into _group_id from drug_group where name = _name;
    if _group_id is null then
        insert into drug_group (name) value (_name);
        select last_insert_id() into _group_id;
    end if;
end;

drop procedure if exists user_delete;
create procedure user_delete(in _user_id int)
begin
    delete from customer_cart_has_item where user_id = _user_id;
    delete from user where user_id = _user_id;
end;


drop procedure if exists manufacturer_add;
create procedure manufacturer_add(
    in _company_name varchar(256),
    in _country_name varchar(256)
)
begin
    declare _country_id int default null;
    declare exit handler for sqlexception begin
        rollback;
        resignal;
    end;
    start transaction;
    call country_get_id(_country_id, _country_name);
    insert into manufacturer (country_id, name) value (_country_id, _company_name);
    commit;
end;

drop procedure if exists manufacturer_delete;
create procedure manufacturer_delete(in _mf_id int)
begin
    declare _country_id int default null;
    declare _country_n_occurrences int default 0;
    select country_id into _country_id from manufacturer where manufacturer_id = _mf_id;
    delete from manufacturer where manufacturer_id = _mf_id;
    select count(*) into _country_n_occurrences from manufacturer where country_id = _country_id;
    if _country_n_occurrences = 0 then
        delete from country where country_id = _country_id;
    end if;
end;


drop procedure if exists drug_add;
create procedure drug_add(
    in _mf_id int,
    in _cipher varchar(256),
    in _group_name varchar(256),
    in _name varchar(256)
)
begin
    declare _group_id int default null;
    declare exit handler for sqlexception begin rollback; resignal; end;
    start transaction;
    call drug_group_get_id(_group_id, _group_name);
    insert into drug (drug_group_id, cipher, name, manufacturer_id) value (_group_id, _cipher, _name, _mf_id);
    commit;
end;

drop procedure if exists drug_delete;
create procedure drug_delete(in _drug_id int)
begin
    declare _group_id int default null;
    declare _group_n_occur int default 0;
    select drug_group_id into _group_id from drug where drug_id = _drug_id;
    delete from drug where drug_id = _drug_id;
    select count(*) into _group_n_occur from drug where drug_group_id = _group_id;
    if _group_n_occur = 0 then
        delete from drug_group where drug_group_id = _group_id;
    end if;
end;


drop procedure if exists vendor_add;
create procedure vendor_add(
    in _cipher varchar(256),
    in _company_name varchar(256),
    in _city_name varchar(256),
    in _conclusion_date date
)
begin
    declare _city_id int;
    declare exit handler for sqlexception begin rollback; resignal; end;
    start transaction;
    call city_get_id(_city_id, _city_name);
    insert into vendor (cipher, company_name, city_id, conclusion_date)
        value (_cipher, _company_name, _city_id, _conclusion_date);
    commit;
end;

drop procedure if exists vendor_delete;
create procedure vendor_delete(in _vendor_id int)
begin
    declare _city_id int default null;
    declare _city_occurrences int default 0;
    select city_id into _city_id from vendor where vendor_id = _vendor_id;
    delete from vendor where vendor_id = _vendor_id;
    select count(*) into _city_occurrences from vendor where city_id = _city_id;
    if _city_occurrences = 0 then
        delete from city where city_id = _city_id;
    end if;
end;


drop procedure if exists vendor_add_item;
create procedure vendor_add_item(
    in _vendor_id int,
    in _item_id int,
    in _amount int
)
begin

end;

