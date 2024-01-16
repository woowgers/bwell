from flask import flash, g


def flash_error(message: str | Exception) -> None:
    flash(str(message), category="error")
    g.error_flashed = True


def error_flashed() -> bool:
    return "error_flashed" in g


def flash_info(message: str) -> None:
    flash(message, category="info")


def flash_success(message: str) -> None:
    flash(message, category="success")
