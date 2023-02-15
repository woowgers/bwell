from dataclasses import dataclass
from datetime import date
from enum import Enum
import typing as t


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
    country_name: str
    name: str


@dataclass
class Vendor:
    vendor_id: int
    cipher: str
    company_name: str
    city_name: str
    conclusion_date: date
    termination_date: t.Optional[date]


@dataclass
class DrugGroup:
    drug_group_id: int
    name: str


@dataclass
class Drug:
    drug_id: int
    drug_group: str
    cipher: str
    name: str
    manufacturer: str


@dataclass
class Item:
    item_id: int
    drug_id: int
    drug_group: str
    drug_cipher: str
    drug_name: str
    drug_manufacturer: str
    price: int


@dataclass
class ItemAmount:
    item_id: int
    drug_id: int
    drug_group: str
    drug_cipher: str
    drug_name: str
    drug_manufacturer: str
    price: int
    amount: int
