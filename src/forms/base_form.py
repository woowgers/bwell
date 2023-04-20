import typing as t
import uuid
from functools import reduce

from helpers import dict_to_snake_case, to_user_friendly
from helpers.flashes import flash_error

from .base_field import Field
from .validators import *


class FormMeta(type):
    def __init__(self, cls_name, cls_bases, cls_dict):  # pyright: ignore
        self._check_prop_methods(cls_name)
        self._create_fields_descs_dict()

    def _check_prop_methods(self, cls_name) -> None:
        prop_methods = ("is_valid", "fields", "invalid_fields")
        for prop_method in prop_methods:
            if callable(getattr(self, prop_method)):
                raise TypeError(
                    f"`{cls_name}.{prop_method}` should be decorated with `@property`"
                )

    def _create_fields_descs_dict(self) -> None:
        self._field_descs: dict[str, Field] = {}
        for field_name, field_desc in self.__dict__.items():
            if isinstance(field_desc, Field):
                self._field_descs[field_name] = field_desc


class Form(metaclass=FormMeta):
    def __init__(
        self,
        action: str = "",
        fields_dict: dict[str, t.Any] | None = None,
        submit_value: str = "",
    ):
        self._fields: dict[str, t.Any] = {}
        self._invalid_fields: dict[str, t.Any] = {}
        self._action: str = action
        self._submit_value: str = submit_value
        self._form_id: str = Form._generate_id()

        if fields_dict:
            self._set_fields_values(fields_dict)

    def _set_fields_values(self, fields_dict: dict[str, t.Any]) -> None:
        fields_dict = dict_to_snake_case(fields_dict)
        field_descs: dict[str, Field] = self.__class__._field_descs
        for field_name, field_desc in field_descs.items():
            field_desc.__set__(self, fields_dict.pop(field_name, None))
            if field_name not in self._fields:
                raise TypeError(
                    f'`{type(self).__name__}.__init__`: Unexpected field name "{field_name}"'
                )

    @classmethod
    def _generate_id(cls) -> str:
        return cls.__name__ + str(uuid.uuid1())

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

    @property
    def html_inputs(self) -> tuple[str]:
        return tuple(
            field_desc.html_input(self._form_id)
            for field_desc in self.__class__._field_descs.values()
        )

    @property
    def html_labels(self) -> tuple[str]:
        return tuple(
            field_desc.html_label(self._form_id)
            for field_desc in self.__class__._field_descs.values()
        )

    @property
    def html_submit(self) -> str:
        return f"""
            <input type="submit" form="{ self._form_id }" value="{ self._submit_value }">
        """

    @property
    def html_form(self) -> str:
        return f"""
            <form method="POST" action="{ self._action }" id="{ self._form_id }">
            </form>
        """

    @property
    def html(self, include_labels: bool = True, include_inputs: bool = True) -> str:
        labels, inputs = self.html_labels, self.html_inputs

        def summer(sum: str, i: int) -> str:
            result = sum
            if include_labels:
                result += labels[i]
            if include_inputs:
                result += inputs[i]
            return result

        content = reduce(summer, range(len(inputs)), "")
        return f"""
            <form method="POST" action="{ self._action }" id="{self._form_id}">
                {content}
                {self.html_submit}
            </form>
        """
