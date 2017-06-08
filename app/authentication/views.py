#! venv/bin/python

from app import app, db

from app.authentication.models import User
from app.authentication.forms import LoginForm

from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response, Blueprint
from functools import wraps
from config import basedir, SQLALCHEMY_DATABASE_URI
import time, os, hashlib, json, datetime

authentication = Blueprint('login', __name__, url_prefix='/login')

#Проверка сессии на логин
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

#Функция проверки доступа пользователя и логин
@authentication.route('/', methods=['GET', 'POST'])
def login():
    form_login = LoginForm()

    if form_login.validate_on_submit():
        login_user = form_login.login.data
        login_password = form_login.password.data

        user_data = User.query.filter(User.login == login_user).first()
        if (user_data):
            if ((user_data.status==1) or (user_data.role.id==1)):
                password_hash = hashlib.md5(login_password)
                if ((user_data.login==login_user) and (user_data.password==password_hash.hexdigest())):
                    session['logged_in'] = True
                    session['user_id'] = user_data.id
                    session['last_login'] = user_data.last_login

                    user_data.last_login = time.strftime("%Y-%m-%d %H:%M:%S")
                    db.session.commit()

                    return redirect(url_for('admin.admin'))
                else:
                    flash(u"Неправильное сочетание логина и пароля, повторите ввод", 'error')
            else:
                flash(u"Ваш пользователь отключен. Пожалуйста, обратитесь к системному администратору", 'error')
        else:
            flash(u"Пользователя с таким логином не существует", 'error')

    return render_template('admin/login.html', form_login=form_login)

#Функция выхода пользователя из сессии
@authentication.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))
