insert into user (user_type, email, name, pw_hash) values
(
    'admin',
    'sashashibaev@gmail.com',
    'alexw00',
    '$2b$12$wm1IqpuZp65dsT2D2UQaGOpVOUUs0QhpEsMRQdIHsKUpIvCXBT4SS'
), (
    'cashier',
    'glebpisarenko@gmail.com',
    'Tt_Tt',
    '$2b$12$IDIVQcP5773uKwaFrwfwPuZfw57dHyJhYe0Yc6KeMUZpyLnV6yhBS'
), (
    'customer',
    'forkcs@geosas.ru',
    'forkcs',
    '$2b$12$5tvwJN.afasoBKfx7UQxU.gMyGm4GyPjkRH4FZp82PqIV7zWB1TkC'
);

call manufacturer_add('BAYER', 'Germany');
call manufacturer_add('Aspen', 'France');
call manufacturer_add('Pfizer', 'America');
call manufacturer_add('R-Pharm', 'Russia');
call manufacturer_add('Biocad', 'Russia');
call manufacturer_add('Generium', 'Russia');
call manufacturer_add('Pharmsintez', 'Russia');

call drug_add(1, uuid(), 'Обезболивающее', 'Аспирин');
call drug_add(1, uuid(), 'Антигистаминное', 'Кларитин');
call drug_add(1, uuid(), 'Слабительное', 'Микролакс');

call drug_add(2, uuid(), 'Антидепрессант', 'Сертралин');
call drug_add(2, uuid(), 'Противовоспалительное', 'Аденозин');

call drug_add(3, uuid(), 'Противовоспалительное', 'Парацетамол');
call drug_add(3, uuid(), 'Противовоспалительное', 'Нурофен');
call drug_add(3, uuid(), 'Транквилизатор', 'Феназепам');
call drug_add(4, uuid(), 'Противовирусное', 'БактоБЛИС плюс');
call drug_add(4, uuid(), 'Антибиотик', 'Спектрацеф');

call drug_add(5, uuid(), 'Противовирусное', 'Илсира');
call drug_add(5, uuid(), 'Противовирусное', 'Альгерон');
call drug_add(5, uuid(), 'Иммуномодулятор', 'Фортека');
call drug_add(5, uuid(), 'Иммуномодулятор', 'Авегра');

call drug_add(6, uuid(), 'Противовирусное', 'Спутник V');
call drug_add(6, uuid(), 'Муколитическое', 'Тигераза');

call drug_add(7, uuid(), 'Противовирусное', 'АЛАГЕТ');
call drug_add(7, uuid(), 'Антибиотик', 'АКВАПЕНЕМ');


call vendor_add(uuid(), 'АРГЕНТУМ', 'Тула', '2020-06-24');
call vendor_add(uuid(), 'Главфарм', 'Москва', '2019-10-14');
call vendor_add(uuid(), 'Alliance Healthcare', 'Москва', '2017-06-07');
call vendor_add(uuid(), 'Медторг', 'Москва', '2018-06-22');
call vendor_add(uuid(), 'Надежда+', 'Санкт-Петербург', '2020-05-06');
call vendor_add(uuid(), 'Русская тройка', 'Краснодар', '2023-02-09');
