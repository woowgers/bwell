def apostrophe_appended(username: str) -> str:
    if username[-1] in "sz":
        return username + "'"
    else:
        return username + "'s"


def to_snake_case(string: str) -> str:
    return string.replace("-", "_").replace(" ", "_")


def dict_to_snake_case(dict_: dict) -> dict:
    dict_snake_cased = {}
    for key, value in dict_.items():
        dict_snake_cased[to_snake_case(key)] = value
    return dict_snake_cased


def to_user_friendly(snake_case: str) -> str:
    return snake_case.capitalize().replace("_", " ")
