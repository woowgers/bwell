import datetime
import typing as t
from dataclasses import dataclass
from enum import Enum


class UserType(Enum):
    ADMIN = "admin"
    CASHIER = "cashier"
    CUSTOMER = "customer"


@dataclass
class User:
    user_id: int
    email: str
    type: UserType
    name: str
    pw_hash: bytes

    @property
    def is_admin(self):
        return self.type == UserType.ADMIN.value

    @property
    def is_cashier(self):
        return self.type == UserType.CASHIER.value

    @property
    def is_customer(self):
        return self.type == UserType.CUSTOMER.value


@dataclass
class Country:
    country_id: int
    name: str


@dataclass
class City:
    city_id: int
    name: str


@dataclass
class Manufacturer:
    manufacturer_id: int
    country: Country
    name: str

    @classmethod
    def from_primitives(
        cls,
        manufacturer_id: int,
        country_id: int,
        country_name: str,
        name: str,
    ) -> t.Self:
        return cls(
            manufacturer_id,
            Country(country_id, country_name),
            name,
        )


@dataclass
class Vendor:
    vendor_id: int
    cipher: str
    company_name: str
    city: City
    conclusion_date: datetime.date
    termination_date: datetime.date | None

    @classmethod
    def from_primitives(
        cls,
        vendor_id: int,
        cipher: str,
        company_name: str,
        city_id: int,
        city_name: str,
        conclusion_date: datetime.date,
        termination_date: datetime.date | None,
    ) -> t.Self:
        return cls(
            vendor_id,
            cipher,
            company_name,
            City(city_id, city_name),
            conclusion_date,
            termination_date,
        )


@dataclass
class DrugGroup:
    drug_group_id: int
    name: str


@dataclass
class Drug:
    drug_id: int
    drug_group: DrugGroup
    cipher: str
    name: str
    manufacturer: Manufacturer

    @classmethod
    def from_primitives(
        cls,
        drug_id: int,
        drug_group_id: int,
        drug_group_name: str,
        cipher: str,
        name: str,
        mf_id: int,
        mf_country_id: int,
        mf_country_name: str,
        mf_name: str,
    ) -> t.Self:
        return cls(
            drug_id,
            DrugGroup(drug_group_id, drug_group_name),
            cipher,
            name,
            Manufacturer.from_primitives(
                mf_id,
                mf_country_id,
                mf_country_name,
                mf_name,
            ),
        )


@dataclass
class Item:
    item_id: int
    drug: Drug
    price: float

    @classmethod
    def from_primitives(
        cls,
        item_id: int,
        drug_id: int,
        drug_group_id: int,
        drug_group_name: str,
        drug_cipher: str,
        drug_name: str,
        drug_mf_id: int,
        drug_mf_country_id: int,
        drug_mf_country_name: str,
        drug_mf_name: str,
        price: float,
    ) -> t.Self:
        return cls(
            item_id,
            Drug.from_primitives(
                drug_id,
                drug_group_id,
                drug_group_name,
                drug_cipher,
                drug_name,
                drug_mf_id,
                drug_mf_country_id,
                drug_mf_country_name,
                drug_mf_name,
            ),
            price,
        )


@dataclass
class Order:
    order_id: int
    user: User
    create_date: datetime.date
    expect_receive_date: datetime.date
    receive_date: datetime.date | None = None
    cost: float | None = 0

    @classmethod
    def from_primitives(
        cls,
        order_id: int,
        user_id: int,
        user_email: str,
        user_type: UserType,
        user_name: str,
        user_pw_hash: bytes,
        create_date: datetime.date,
        expect_receive_date: datetime.date,
        receive_date: t.Optional[datetime.date],
        cost: float,
    ) -> t.Self:
        return cls(
            order_id,
            User(user_id, user_email, user_type, user_name, user_pw_hash),
            create_date,
            expect_receive_date,
            receive_date,
            cost,
        )
