#coding=utf-8
import logging.config
from config import Config
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_msearch import Search
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
csrf = CSRFProtect()
csrf.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
moment = Moment(app)
search = Search()
search.init_app(app)
mail = Mail(app)


from app import errors, models, routes


logging.config.dictConfig(app.config['LOG_CONFIG'])
logger = logging.getLogger('chardet.charsetprober')
logger.setLevel(logging.INFO)

# 创建管理员用户
admin = models.User(
    username      = 'admin',
    email         = '',
    password_hash = generate_password_hash('admin'),
    admin         = True
)
try:
    db.session.add(admin)
    db.session.commit()
except:
    db.session.rollback()