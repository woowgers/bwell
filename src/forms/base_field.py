from .validators import *

from abc import ABC, abstractmethod
import typing as t

from helpers import to_user_friendly
from .base_form import Form


class Field(ABC):
    def __init__(self, required: bool = True, input_type: str = "text"):
        self.required = required
        self.input_type = input_type

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

    def html_label(self, form_id: str) -> str:
        return f"""
            <label for="{self.name}" form="{form_id}">
                {to_user_friendly(self.name)}
            </label>
        """

    def html_input(self, form_id: str) -> str:
        return f"""
            <input
                name="{self.name}"
                type="{self.input_type}"
                form="{form_id}"
            >
        """

    def html(self, form_id: str) -> str:
        return self.html_label(form_id) + self.html_input(form_id)
