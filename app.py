from flask import Flask
from blueprints.admin import admin_blueprint
from blueprints.users import users_blueprint


app = Flask(__name__)

app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(users_blueprint, url_prefix='/users')

if __name__ == '__main__':
    app.run(debug=True)
