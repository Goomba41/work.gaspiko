from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_sse import sse

app = Flask(__name__)
app.config.from_object('config')
app.config["REDIS_URL"] = "redis://localhost:6379"
app.register_blueprint(sse, url_prefix='/stream')

db = SQLAlchemy (app)
migrate = Migrate (app, db)

from config import basedir
from app import views, models

