import typing as t
from db.models import User, UserType
import re

from datetime import datetime


def any_is_valid(_: t.Any) -> bool:
    return True


USER_TYPE_REQUIREMENTS = f"""
    User type must be one of: {UserType.ADMIN.value}, {UserType.CASHIER.value}, {UserType.CUSTOMER.value}.
"""


def user_type_is_valid(user_type_value: t.Any) -> bool:
    if isinstance(user_type_value, UserType):
        return True
    try:
        UserType(user_type_value)
        return True
    except ValueError:
        return False


def user_is_valid(user_value: t.Any) -> bool:
    if isinstance(user_value, User):
        return True
    try:
        User(**user_value)
        return True
    except (TypeError, ValueError):
        return False


EMAIL_REQUIREMENTS = """
    Email has to satisfy regular expression: \\w+@\\w+.(com|ru).
    For example, myname@myemail.ru
"""


def email_is_valid(email_str: t.Any) -> bool:
    email_pattern = r"\w+@\w+.(com|ru)"
    return (
        isinstance(email_str, str)
        and re.fullmatch(email_pattern, email_str) is not None
    )


PASSWORD_LENGTH_MIN = 6
PASSWORD_REQUIREMENTS = f"""
    Password must contain uppercase, lowercase latin letters, digits,
    special characters and be at least {PASSWORD_LENGTH_MIN} characters length.
"""


def password_is_valid(password_str: t.Any) -> bool:
    if not isinstance(password_str, str) or len(password_str) < PASSWORD_LENGTH_MIN:
        return False
    patterns = r"[a-z]", r"[A-Z]", r"[0-9]", r'[_~!@#$%^&*()+-=[\]{}\\|;:\'";:/?.>,<]'
    return all(map(lambda pattern: re.search(pattern, password_str), patterns))


USERNAME_LENGTH_MIN = 4
USERNAME_LENGTH_MAX = 255
USERNAME_REQUIREMENTS = f"""
    Username can only contain uppercase or lowercase latin letters, digits, underscore or dash.
    It's length must be between {USERNAME_LENGTH_MIN} and {USERNAME_LENGTH_MAX}.
"""


def username_is_valid(username_str: t.Any) -> bool:
    pattern = rf"[-_a-zA-Z0-9]{{{USERNAME_LENGTH_MIN},{USERNAME_LENGTH_MAX}}}"
    if not isinstance(username_str, str):
        return False
    return re.fullmatch(pattern, username_str) is not None


DATE_REQUIREMENTS = f"Date must be in form: YYYY-MM-DD."


def date_is_valid(date_str: t.Any) -> bool:
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
