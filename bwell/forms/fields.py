import math
import typing as t
import uuid

from bwell.forms.base import Field, Form
from bwell.forms.validators import *
from bwell.helpers import to_user_friendly


class BooleanField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, input_type="checkbox")

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
    def __init__(
        self,
        minlen: int = 0,
        maxlen: int = t.cast(int, math.inf),
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if minlen > maxlen:
            raise ValueError(
                f"{to_user_friendly(self.name)} minimum length must not be greater than maximum length.",
            )
        self.minlen = minlen
        self.maxlen = maxlen

    def is_valid(self, value) -> bool:
        if value is None:
            return True
        return (
            isinstance(value, str) and self.minlen <= len(value) <= self.maxlen
        )

    @property
    def validation_requirements(self) -> str:
        return f"{to_user_friendly(self.name)} must be string with length between specified limits."


class IntegerField(Field):
    def __init__(
        self,
        minval: int = t.cast(int, -math.inf),
        maxval: int = t.cast(int, math.inf),
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs, input_type="number")
        if minval > maxval:
            raise ValueError(
                f'"{to_user_friendly(self.name)}" minimum value must not be greater than maximum value.',
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

    # def __get__(self, obj, _=None) -> t.Union[int, "IntegerField", None]:
    def __get__(self, obj, _=None) -> int:
        return int(obj._fields[self.name])

    @property
    def validation_requirements(self) -> str:
        return f"{to_user_friendly(self.name)} value must be integer in interval [{self.minval}; {self.maxval}]."


class FloatField(Field):
    def __init__(
        self,
        minval: float = float(-math.inf),
        maxval: float = float(math.inf),
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs, input_type="number")
        if minval > maxval:
            raise ValueError(
                f'"{to_user_friendly(self.name)}" must not be greater than maximum value.',
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, input_type="email")

    def is_valid(self, value) -> bool:
        return email_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return EMAIL_REQUIREMENTS


class PasswordField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, input_type="password")

    def is_valid(self, value) -> bool:
        return password_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return PASSWORD_REQUIREMENTS


class UsernameField(StringField):
    def is_valid(self, value) -> bool:
        return username_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return USERNAME_REQUIREMENTS


class UserTypeField(StringField):
    def is_valid(self, value) -> bool:
        return user_type_is_valid(value)

    @property
    def validation_requirements(self) -> str:
        return USER_TYPE_REQUIREMENTS


class DateField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, input_type="date")

    def is_valid(self, value) -> bool:
        if value is None:
            return True
        return date_is_valid(value)

    def __get__(
        self,
        obj: Form,
        _=None,
    ) -> t.Union[datetime.date, "DateField", None]:
        if obj._fields[self.name]:
            try:
                return date_from_string(obj._fields[self.name])
            except ValueError:
                return self

    @property
    def validation_requirements(self) -> str:
        return DATE_REQUIREMENTS


class CipherField(StringField):
    def is_valid(self, value):
        return isinstance(value, str) and len(value) >= 6

    def __set__(self, obj: Form, value: t.Any):
        if value == "$UUID":
            value = str(uuid.uuid1())
        super().__set__(obj, value)

    @property
    def validation_requirements(self) -> str:
        return f'"{self.name}" must be string at least 6 character length.'
