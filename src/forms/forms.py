from db.models import Order
from helpers.flashes import flash_error

from .base_form import Form
from .fields import *


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
            self.checkers.append(
                lambda order: order.receive_date >= self.receive_date_min
            )
        if self.receive_date_max:
            self.checkers.append(
                lambda order: order.receive_date <= self.receive_date_max
            )
        if self.create_date_min:
            self.checkers.append(
                lambda order: order.create_date >= self.create_date_min
            )
        if self.create_date_max:
            self.checkers.append(
                lambda order: order.create_date <= self.create_date_max
            )
        if self.cost_min:
            self.checkers.append(lambda order: order.cost >= self.cost_min)
        if self.cost_max:
            self.checkers.append(lambda order: order.cost <= self.cost_max)

    @property
    def is_valid(self) -> bool:
        is_valid = super().is_valid
        if not self.is_received and (self.receive_date_min or self.receive_date_max):
            flash_error(
                "Either choose range of receive date, or set `Is received` to false."
            )
            is_valid = False
        if (
            isinstance(self.cost_min, float)
            and isinstance(self.cost_max, float)
            and self.cost_min > self.cost_max
        ):
            flash_error("Minimum cost must not be greater than maximum cost.")
            is_valid = False
        if (
            isinstance(self.create_date_min, datetime.date)
            and isinstance(self.create_date_max, datetime.date)
            and self.create_date_min > self.create_date_max
        ):
            flash_error(
                "Minimum create date must not be greater than maximum create date."
            )
            is_valid = False
        if (
            isinstance(self.receive_date_min, datetime.date)
            and isinstance(self.receive_date_max, datetime.date)
            and self.receive_date_min > self.receive_date_max
        ):
            flash_error(
                "Minimum receive date must not be greater than maximum receive date."
            )
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
