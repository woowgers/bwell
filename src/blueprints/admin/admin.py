from flask import Blueprint

admin = Blueprint('admin', __name__)


@admin.route('/')
def root():
    return "Welcome to admin page!"


@admin.route('/blueprint_dependent_greeting')
def greeting():
    return "Hello, admin!"
