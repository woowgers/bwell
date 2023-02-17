from .validators import *

from abc import ABC, abstractmethod
import typing as t
import uuid
import math

from helpers.flashes import flash_error
from helpers import dict_to_snake_case, to_user_friendly


"""
 -- Bases --
"""


class Field(ABC):
    """
    Base descriptor class for fields.

    Derived classes should implement
    """

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

        self._field_descs = {}

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
            if field_value is None:
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


class StringField(Field):
    def __init__(self, minlen: int = 0, maxlen: int = t.cast(int, math.inf)):
        if minlen > maxlen:
            raise ValueError(
                f"{to_user_friendly(self.name)} minimum length must not be greater than maximum length."
            )
        self.minlen = minlen
        self.maxlen = maxlen

    def is_valid(self, value) -> bool:
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
        self, minval: float = float(-math.inf), maxval: float = float(math.inf)
    ):
        if minval > maxval:
            raise ValueError(
                f'"{to_user_friendly(self.name)}" must not be greater than maximum value.'
            )
        self.minval = minval
        self.maxval = maxval

    def is_valid(self, value) -> bool:
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


class AddItemToCartFormWithID(Form):
    item_id = IntegerField()
    amount = IntegerField(minval=1)


class ChangeItemAmountForm(Form):
    item_id = IntegerField()
    amount = IntegerField(minval=0)
