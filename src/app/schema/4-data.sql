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
    '$2b$12$6NOxKTcNytW1UzsZgQesveXckfJD0xilOq41zP6k3aF1ed0DxyFOO'
), (
    'customer',
    'forkcs@geosas.ru',
    'forkcs',
    '$2b$12$6NOxKTcNytW1UzsZgQesveXckfJD0xilOq41zP6k3aF1ed0DxyFOO'
);

insert into country (name) values
('Russia'),
('Germany'),
('France'),
('America');

insert into manufacturer (country_id, name) values
(2, 'BAYER'),
(3, 'Aspen'),
(4, 'Pfizer'),
(1, 'R-Pharm'),
(1, 'Biocad'),
(1, 'Generium'),
(1, 'Pharmsintez');

insert into drug_group (name) values
('Обезболивающее'),
('Антигистаминное'),
('Слабительное'),
('Антидепрессант'),
('Противовоспалительное'),
('Успокоительное'),
('Антибиотик'),
('Противовирусное'),
('Иммуномодулятор'),
('Муколитическое');


insert into drug (drug_group_id, cipher, name, manufacturer_id) values
(1, uuid(), 'Аспирин', 1),
(1, uuid(), 'Аспирин', 2),
(1, uuid(), 'Аспирин', 3),
(2, uuid(), 'Кларитин', 1),
(3, uuid(), 'Микролакс', 1),
(4, uuid(), 'Сертралин', 2),
(5, uuid(), 'Аденозин', 2),
(5, uuid(), 'Аденозин', 4),
(1, uuid(), 'Парацетамол', 3),
(1, uuid(), 'Парацетамол', 5),
(1, uuid(), 'Нурофен', 3),
(6, uuid(), 'Феназепам', 3),
(8, uuid(), 'БактоБЛИС плюс', 4),
(7, uuid(), 'Спектрацеф', 4),
(8, uuid(), 'Илсира', 5),
(8, uuid(), 'Альгерон', 5),
(9, uuid(), 'Фортека', 5),
(9, uuid(), 'Авегра', 5),
(8, uuid(), 'Спутник V', 6),
(10, uuid(), 'Тигераза', 6),
(8, uuid(), 'АЛАГЕТ', 7),
(7, uuid(), 'АКВАПЕНАМ', 7);


insert into city (name) values
('Москва'),
('Тула'),
('Санкт-Петербург'),
('Краснодар');
select * from city order by city_id;

insert into vendor (cipher, company_name, city_id, conclusion_date) values
(uuid(), 'АРГЕНТУМ', 2, '2020-06-24'),
(uuid(), 'Главфарм', 1, '2019-10-14'),
(uuid(), 'Alliance Healthcare', 1, '2017-06-07'),
(uuid(), 'Медторг', 1, '2018-06-22'),
(uuid(), 'Надежда+', 3, '2020-05-06'),
(uuid(), 'Русская тройка', 4, '2023-02-09');
