drop procedure if exists get_country_create_if_not_exists;
create procedure get_country_create_if_not_exists(
    inout _country_id integer,
    inout _name varchar(256)
)
    language plpgsql
    as $$
begin
    select country_id into _country_id from country where name = _name;
    if _country_id is null then
        insert into country (name) values (_name) returning country_id;
        select lastval() into _country_id;
    end if;
    commit;
end $$;
