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
