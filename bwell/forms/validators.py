import datetime
import re
import string
from typing import Any

from bwell.db.models import UserType


def date_from_string(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def any_is_valid(_) -> bool:
    return True


USER_TYPE_REQUIREMENTS = (
    f'User type must be one of: {UserType.ADMIN.value}, '
    f'{UserType.CASHIER.value}, {UserType.CUSTOMER.value}.'
)


def user_type_is_valid(user_type_value: str) -> bool:
    if isinstance(user_type_value, UserType):
        return True
    try:
        UserType(user_type_value)
    except ValueError:
        return False
    else:
        return True


EMAIL_REQUIREMENTS = (
    'Email has to satisfy regular expression: \\w+@\\w+.(com|ru). '
    'For example, myname@myemail.ru.'
)


def email_is_valid(email_str: str) -> bool:
    email_pattern = r"\w+@\w+.(com|ru)"
    return (
        isinstance(email_str, str)
        and re.fullmatch(email_pattern, email_str) is not None
    )


PASSWORD_LENGTH_MIN = 6
PASSWORD_REQUIREMENTS = (
    'Password must contain uppercase, lowercase latin letters, digits,'
    f'special characters and be at least {PASSWORD_LENGTH_MIN} '
    'characters length.'
)


def password_is_valid(password_str: Any) -> bool:
    def make_pattern(allowed_characters: str) -> str:
        return f'[{re.escape(allowed_characters)}]'

    patterns = map(
        make_pattern,
        (
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.digits,
            string.punctuation,
        ),
    )
    matches = (re.search(pattern, password_str) for pattern in patterns)
    return (
        isinstance(password_str, str)
        and len(password_str) >= PASSWORD_LENGTH_MIN
        and all(matches)
    )


USERNAME_LENGTH_MIN = 4
USERNAME_LENGTH_MAX = 255
USERNAME_REQUIREMENTS = (
    f'Username can only contain uppercase or lowercase latin letters, digits,'
    'underscore or dash. It\'s length must be between'
    f'{USERNAME_LENGTH_MIN} and {USERNAME_LENGTH_MAX}.'
)


def username_is_valid(username_str: Any) -> bool:
    pattern = rf"[-_a-zA-Z0-9]{{{USERNAME_LENGTH_MIN},{USERNAME_LENGTH_MAX}}}"
    if not isinstance(username_str, str):
        return False
    return re.fullmatch(pattern, username_str) is not None


DATE_REQUIREMENTS = 'Date must be in form: YYYY-MM-DD.'


def date_is_valid(date_str: Any) -> bool:
    if isinstance(date_str, datetime.date):
        return True

    if isinstance(date_str, str):
        try:
            date_from_string(date_str)
        except ValueError:
            return False
        else:
            return True

    return False
