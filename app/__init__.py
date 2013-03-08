# App (Flask)
from flask import Flask
app = Flask(__name__)
app.config.from_object("config")

# Debug Mailing
from config import ADMINS, MAIL_PASSWORD, MAIL_PORT, MAIL_SERVER, MAIL_USERNAME
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@creco.co', ADMINS, 'ThanksPress Failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# Debug Toolbar
from flask_debugtoolbar import DebugToolbarExtension
app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

# LoginManager
from flask.ext.login import LoginManager
lm = LoginManager()
lm.setup_app(app)
lm.login_view = 'login'
lm.login_message = 'You must login to access this page.'

# Mail
from flask.ext.mail import Mail
mail = Mail(app)

# SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

#App
from app import before_request
from app import error_handlers

# Apps
from config import APPS
for _app in APPS:
    __import__("app.%s.views" % _app)
    __import__("app.%s.models" % _app)