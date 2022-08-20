from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = "VerySecret"
bcrypt = Bcrypt(app)
loginMana = LoginManager(app)
loginMana.login_view = 'login'

# db connection for mysql database
# replace what's inside <> with your info, remove <>
dburi = "mysql+pymysql://<username>:<password>@<server>/<dbname>"
app.config['SQLALCHEMY_DATABASE_URI'] = dburi
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
engine = create_engine(dburi)
conn = engine.connect()
###################################

# db connection for sqlite database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pbook.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# You may need to change some sql statements to make it work with sqlite
# Also need to init a cursor for sqlite

# Avoid circular reference
from pbook import routes
