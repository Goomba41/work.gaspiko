#! env/bin/python3.8

from app import app, db

from app.models import User

from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response, Blueprint
from functools import wraps
from urllib.parse import urlparse, urljoin
import time, os, hashlib, json, datetime


authentication = Blueprint('login', __name__, url_prefix='/login')

#Проверка URL
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

#Проверка сессии на логин
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#Отображение шаблона логина
@authentication.route('/')
def login():
    return render_template('admin/login.html')

#Функция проверки доступа пользователя и логин
@authentication.route('/login-process', methods=['GET', 'POST'])
def login_process():
    
    login_user = request.form['login']
    login_password = request.form['password']

    # Подумать над запросом пользователя через API
    user = User.query.filter(User.login == login_user).first()
    if user:
        if ((user.status==1) or (user.role.id==1)):
            password_hash = hashlib.md5(login_password.encode("utf-8"))
            if ((user.login==login_user) and (user.password==password_hash.hexdigest())):
                session['logged_in'] = True
                session['user_id'] = user.id
                session['last_login'] = user.last_login

                user.last_login = time.strftime("%Y-%m-%d %H:%M:%S")
                db.session.commit()
                
                next = request.args.get('next')
                if not is_safe_url(next) or next is None:
                    next = url_for("admin.admin")

                response = Response(
                response=json.dumps({'next':str(next)}),
                status=200,
                mimetype='application/json'
                )
            else:
                response = Response(
                response=json.dumps({'result':"Неправильное сочетание логина и пароля, повторите ввод!"}),
                status=403,
                mimetype='application/json'
                )
        else:
            response = Response(
            response=json.dumps({'result':"Ваш пользователь отключен. Пожалуйста, обратитесь к системному администратору!"}),
            status=403,
            mimetype='application/json'
            )
    else:
        response = Response(
        response=json.dumps({'result':"Пользователя с таким логином не существует!"}),
        status=404,
        mimetype='application/json'
        )
    
    return response

#Функция выхода пользователя из сессии
@authentication.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))
