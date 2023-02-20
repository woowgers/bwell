from .validators import *

from abc import ABC, abstractmethod
import typing as t
import uuid
import math

from helpers.flashes import flash_error
from helpers import dict_to_snake_case, to_user_friendly

from db.models import Order


"""
 -- Bases --
"""


class Field(ABC):
    def __init__(self, required=True):
        self.required = required

    def __set_name__(self, owner: "Form", name: str):
        if not isinstance(owner, type) or not issubclass(owner, Form):
            raise TypeError(
                f"`{self.__class__.__name__}` must be a class memeber of `Form` subclass"
            )
        self.name = name

    def __set__(self, obj: "Form", value: t.Any):
        obj._fields[self.name] = value
        field_value = getattr(obj, self.name)
        if self.is_valid(field_value):
            obj._invalid_fields.pop(self.name, None)
        else:
            obj._invalid_fields[self.name] = field_value

    def __get__(self, obj: "Form", _=None) -> t.Union[str, "Field", None]:
        if obj._fields[self.name]:
            try:
                return str(obj._fields[self.name])
            except ValueError:
                return self

    @abstractmethod
    def is_valid(self, value) -> bool:
        ...

    @property
    @abstractmethod
    def validation_requirements(self) -> str:
        ...


class FormMeta(type):
    def __init__(self, cls_name, cls_bases, cls_dict):  # pyright: ignore
        prop_methods = ("is_valid", "fields", "invalid_fields")
        for prop_method in prop_methods:
            if callable(getattr(self, prop_method)):
                raise TypeError(
                    f"`{cls_name}.{prop_method}` should be decorated with `@property`"
                )

        self._field_descs: dict[str, Field] = {}

        for field_name, field_desc in self.__dict__.items():
            if isinstance(field_desc, Field):
                self._field_descs[field_name] = field_desc


class Form(metaclass=FormMeta):
    def __init__(self, fields_dict=None):
        fields_dict = fields_dict or {}
        self._fields: dict[str, t.Any] = {}
        self._invalid_fields: dict[str, t.Any] = {}
        fields_dict = dict_to_snake_case(fields_dict)
        field_descs: dict[str, Field] = self.__class__._field_descs
        for field_name, field_desc in field_descs.items():
            field_desc.__set__(self, fields_dict.pop(field_name, None))

        for field_name in fields_dict:
            if field_name not in self._fields:
                raise TypeError(
                    f'`{type(self).__name__}.__init__`: Unexpected field name "{field_name}"'
                )

    def _on_none_field(self, field_name: str) -> None:
        flash_error(f'"{to_user_friendly(field_name)}" is required.')

    def _on_invalid_field(self, field_name: str, field: Field) -> None:
        flash_error(
            f'"{to_user_friendly(field_name)}" is invalid. {field.validation_requirements}'
        )

    @property
    def is_valid(self) -> bool:
        field_descs = self.__class__._field_descs
        for field_name, field_value in self._invalid_fields.items():
            if field_value is None and self.__class__._field_descs[field_name].required:
                self._on_none_field(field_name)
            else:
                self._on_invalid_field(field_name, field_descs[field_name])
        return len(self._invalid_fields) == 0

    @property
    def fields(self) -> dict[str, t.Any]:
        return self._fields

    @property
    def invalid_fields(self) -> dict[str, t.Any]:
        return self._invalid_fields


"""
 -- Fields --
"""


class BooleanField(Field):
    def __get__(self, obj: Form, _=None) -> t.Union[bool, None, "BooleanField"]:
        value = obj._fields[self.name]
        if value:
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False
                

    def is_valid(self, value):
        if value is None:
            return True
        if not isinstance(value, str) and not isinstance(value, bool):
            return False
        try:
            bool(value)
            return True
        except (ValueError, TypeError):
            return False

    @property
    def validation_requirements(self) -> str:
        return f"{to_user_friendly(self.name)} must be either set to true/false or unset."


class StringField(Field):
    def __init__(self, minlen: int = 0, maxlen: int = t.cast(int, math.inf), *args, **kwargs):
        super().__init__(*args, **kwargs)
        if minlen > maxlen:
            raise ValueError(
                f"{to_user_friendly(self.name)} minimum length must not be greater than maximum length."
            )
        self.minlen = minlen
        self.maxlen = maxlen

    def is_valid(self, value) -> bool:
        if value is None:
            return True
        return isinstance(value, str) and self.minlen <= len(value) <= self.maxlen

    @property
    def validation_requirements(self) -> str:
        return f"{to_user_friendly(self.name)} must be string with length between specified limits."


class IntegerField(Field):
    def __init__(
        self, minval: int = t.cast(int, -math.inf), maxval: int = t.cast(int, math.inf)
    ):
        if minval > maxval:
            raise ValueError(
                f'"{to_user_friendly(self.name)}" minimum value must not be greater than maximum value.'
            )
        self.minval = minval
        self.maxval = maxval

    def is_valid(self, value) -> bool:
        if value is None:
            return True
        try:
            return self.minval <= int(value) <= self.maxval
        except (TypeError, ValueError):
            return False

    def __get__(self, obj, _=None) -> t.Union[int, "IntegerField", None]:
        if obj._fields[self.name]:
            try:
                return int(obj._fields[self.name])
            except ValueError:
                return self

    @property
    def validation_requirements(self) -> str:
        return f"{to_user_friendly(self.name)} value must be integer in interval [{self.minval}; {self.maxval}]."


class FloatField(Field):
    def __init__(
        self, minval: float = float(-math.inf), maxval: float = float(math.inf), required=True
    ):
        super().__init__(required)
        if minval > maxval:
            raise ValueError(
                f'"{to_user_friendly(self.name)}" must not be greater than maximum value.'
            )
        self.minval = minval
        self.maxval = maxval

    def is_valid(self, value) -> bool:
        if value is None:
            return True
        try:
            return self.minval <= float(value) <= self.maxval
        except (TypeError, ValueError):
            return False

    def __get__(self, obj: Form, _=None) -> t.Union[float, "FloatField", None]:
        if obj._fields[self.name]:
            try:
                return float(obj._fields[self.name])
            except ValueError:
                return self

    @property
    def validation_requirements(self) -> str:
        return f"{to_user_friendly(self.name)} value must be decimal in range [{self.minval}; {self.maxval}]."


class EmailField(Field):
    def is_valid(self, value) -> bool:
        return email_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return EMAIL_REQUIREMENTS


class PasswordField(Field):
    def is_valid(self, value) -> bool:
        return password_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return PASSWORD_REQUIREMENTS


class UsernameField(Field):
    def is_valid(self, value) -> bool:
        return username_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return USERNAME_REQUIREMENTS


class UserTypeField(Field):
    def is_valid(self, value) -> bool:
        return user_type_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return USER_TYPE_REQUIREMENTS


class DateField(Field):
    def is_valid(self, value) -> bool:
        if value is None:
            return True
        return date_is_valid(value)

    def __get__(self, obj: Form, _=None) -> t.Union[datetime.date, "DateField", None]:
        if obj._fields[self.name]:
            try:
                return date_from_string(obj._fields[self.name])
            except ValueError:
                return self

    @property
    def validation_requirements(self) -> str:
        return DATE_REQUIREMENTS


class CipherField(Field):
    def is_valid(self, value):
        return isinstance(value, str) and len(value) >= 6

    def __set__(self, obj: Form, value: t.Any):
        if value == "$UUID":
            value = str(uuid.uuid1())
        super().__set__(obj, value)

    @property
    def validation_requirements(self) -> str:
        return f'"{self.name}" must be string at least 6 character length.'


"""
 -- Forms --
"""


class RegisterForm(Form):
    user_type = UserTypeField()
    email = EmailField()
    username = UsernameField()
    password = PasswordField()
    repeat_password = PasswordField()

    def _on_nonmatching_passwords(self):
        flash_error("Passwords do not match.")

    @property
    def is_valid(self):
        is_valid = super().is_valid
        if self.password != self.repeat_password:
            self._on_nonmatching_passwords()
            is_valid = False
        return is_valid


class LoginForm(Form):
    email = EmailField()
    password = PasswordField()


class ManufacturerAddForm(Form):
    country_name = StringField()
    company_name = StringField()


class VendorRegisterForm(Form):
    cipher = CipherField()
    company_name = StringField()
    city_name = StringField()
    agreement_conclusion_date = DateField()


class VendorAgreementTerminationForm(Form):
    termination_date = DateField()


class DrugRegisterForm(Form):
    manufacturer_name = StringField()
    cipher = CipherField()
    drug_group_name = StringField()
    drug_name = StringField()


class VendorAddItemForm(Form):
    drug_id = IntegerField()
    price = FloatField()


class VendorAddStorefrontItemForm(Form):
    item_id = IntegerField()
    amount = IntegerField()


class AddItemToCartForm(Form):
    amount = IntegerField(minval=1)


class AddItemToCustomerCartForm(Form):
    drug_id = IntegerField()
    price = FloatField()
    amount = IntegerField(minval=1)


class ChangeItemAmountForm(Form):
    item_id = IntegerField()
    amount = IntegerField(minval=0)


class ChangeCustomerCartItemAmountForm(Form):
    drug_id = IntegerField()
    price = FloatField()
    amount = IntegerField()


class OrderFilterForm(Form):
    create_date_min = DateField(required=False)
    create_date_max = DateField(required=False)
    receive_date_min = DateField(required=False)
    receive_date_max = DateField(required=False)
    cost_min = FloatField(required=False)
    cost_max = FloatField(required=False)
    is_received = BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkers = []
        if self.receive_date_min:
            self.checkers.append(lambda order: order.receive_date >= self.receive_date_min)
        if self.receive_date_max:
            self.checkers.append(lambda order: order.receive_date <= self.receive_date_max)
        if self.create_date_min:
            self.checkers.append(lambda order: order.create_date >= self.create_date_min)
        if self.create_date_max:
            self.checkers.append(lambda order: order.create_date <= self.create_date_max)
        if self.cost_min:
            self.checkers.append(lambda order: order.cost >= self.cost_min)
        if self.cost_max:
            self.checkers.append(lambda order: order.cost <= self.cost_max)

    @property
    def is_valid(self) -> bool:
        is_valid = super().is_valid
        if not self.is_received and (self.receive_date_min or self.receive_date_max):
            flash_error("Either choose range of receive date, or set `Is received` to false.")
            is_valid = False
        if (isinstance(self.cost_min, float) and isinstance(self.cost_max, float) and self.cost_min > self.cost_max):
            flash_error("Minimum cost must not be greater than maximum cost.")
            is_valid = False
        if (isinstance(self.create_date_min, datetime.date) and isinstance(self.create_date_max, datetime.date) and self.create_date_min > self.create_date_max):
            flash_error("Minimum create date must not be greater than maximum create date.")
            is_valid = False
        if (isinstance(self.receive_date_min, datetime.date) and isinstance(self.receive_date_max, datetime.date) and self.receive_date_min > self.receive_date_max):
            flash_error("Minimum receive date must not be greater than maximum receive date.")
            is_valid = False

        return is_valid


    def filter(self, order: Order) -> bool:
        for checker in self.checkers:
            if not checker(order):
                return False
        return True


class DrugFilterForm(Form):
    drug_group_name = StringField(required=False)
    price_min = FloatField(required=False)
    price_max = FloatField(required=False)

