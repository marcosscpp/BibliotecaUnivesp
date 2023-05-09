from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

application = Flask(__name__)
application.config.from_pyfile("configs.py")

banco_de_dados = SQLAlchemy(application)

csrf = CSRFProtect(application)

from views import *
from views_adm import *
from views_user import *

if __name__ == "__main__":
    application.run(debug=True)