#! venv/bin/python

from app import app, db
from models import User, Department, Role, Post, Important_news
from forms import LoginForm, DelUserForm, AddUserForm
from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify
from functools import wraps
from config import basedir, PER_PAGE, SQLALCHEMY_DATABASE_URI
from flask_paginate import Pagination
from sqlalchemy import create_engine
import time, calendar, os, hashlib, shutil

#Функция счета стажа
def standing(f):
    now = str(time.strftime("%Y-%m-%d"))
    first = str(f)
    now = now.split('-')
    first = first.split('-')

    date_first = (int(now[0]),int(now[1]),int(now[2]))
    date_last =  (int(first[0]),int(first[1]),int(first[2]))
    date_result = [date_first[0]-date_last[0],date_first[1]-date_last[1],date_first[2]-date_last[2]]

    if date_result[2] <=0:
        date_result[1] -= 1
        month = date_first[1] - 1
        if month == 0:
            month = 1
        days = calendar.monthrange(date_first[0], month)
        date_result[2] = days[1] + date_result[2]
        if date_result[2] == days[1]:
            date_result[2] = 0
            date_result[1] += 1
    if date_result[1] <=0:
        date_result[0] = date_result[0] - 1
        date_result[1] = date_result[1] + 12
        if date_result[1] == 12:
            date_result[0] += 1
            date_result[1] = 0
    return date_result

#Текущий пользователь
def get_current_user():
    current_user = User.query.filter(User.id == session['user_id']).first()
    return current_user

#Проверка сессии на логин
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#Обработчик ошибки 403 - доступ запрещен
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

#Функция проверки доступа пользователя и логин
@app.route('/login', methods=['GET', 'POST'])
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

                    return redirect(url_for('admin'))
                else:
                    flash(u"Неправильное сочетание логина и пароля, повторите ввод", 'error')
            else:
                flash(u"Ваш пользователь отключен. Пожалуйста, обратитесь к системному администратору", 'error')
        else:
            flash(u"Пользователя с таким логином не существует", 'error')

    return render_template('admin/login.html', form_login=form_login)

#Функция выхода пользователя из сессии
@app.route("/logout")
def logout():
    session.clear()
    return redirect('index')

#Главная (и единственная) страница
@app.route('/')
@app.route('/index')
def index():
    users_all = User.query.all()
    return render_template("work/index.html", users_all = users_all)

#Админка основной экран
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    current_user = get_current_user()
    time_worked = standing(current_user.work_date)

    users_all = User.query.all()
    users_all_count = User.query.count()
    birth_celebrate = {}
    worktime_celebrate = {}
    today = time.strftime("%Y-%m-%d")

    important_news_all = Important_news.query.all()

    for user in users_all:
        if user.birth_date.month ==  int(time.strftime("%m")):
            birth_celebrate.update({'%s %s %s'%(user.surname, user.name, user.patronymic):'%s'%(user.birth_date.day)})
        if user.work_date.month ==  int(time.strftime("%m")):
            worktime_celebrate.update({'%s %s %s'%(user.surname, user.name, user.patronymic):'%s'%(user.work_date.day)})

    return render_template("admin/admin.html",  current_user=current_user, last_login=session['last_login'], time_worked = time_worked, birth_celebrate=birth_celebrate,
    worktime_celebrate=worktime_celebrate, today=today, users_all_count=users_all_count, important_news_all=important_news_all)

@app.route('/admin/users', methods=['GET', 'POST'])
@app.route('/admin/users/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_users(page = 1, *args):

    current_user = get_current_user()
    if current_user.role.id != 1:
        return forbidden(403)

    users_all = User.query.order_by(User.id.asc()).paginate(page, PER_PAGE, False)
    users_all_count = User.query.count()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = users_all_count, per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelUserForm()

    if form_delete.validate_on_submit():
        user_id = form_delete.del_id.data
        User.query.filter(User.id == user_id).delete()
        db.session.commit()
        flash(u"Пользователь удален", 'success')
        return redirect(url_for('admin_users', page = page))

    return render_template("admin/list_users.html", users_all = users_all, users_all_count = users_all_count, pagination = pagination,  current_user=current_user, today=today,
     form_delete=form_delete)

#Сброс и установка нового пароля для пользователя
@app.route('/password_reset', methods = ['POST'])
def get_post_javascript_data_password():
    new_password = request.form['new_password']
    user = request.form['user']

    user_change = User.query.filter(User.id == user).first()
    password_hash = hashlib.md5(new_password).hexdigest()
    user_change.password = password_hash
    db.session.commit()

    return jsonify(password_hash)

#Удаление нескольких записей
@app.route('/rows_delete', methods = ['POST'])
def get_post_javascript_data_id_delete():
    ids = request.form.getlist('param[]')
    if ids:
        users = User.query.filter(User.id.in_(ids)).all()
        for user in users:
            db.session.delete(user)
            db.session.commit()
        return jsonify(ids)
    return jsonify("Не выбраны записи")

#Удаление нескольких записей
@app.route('/rows_disable', methods = ['POST'])
def get_post_javascript_data_id_disable():
    ids = request.form.getlist('param[]')
    if ids:
        users = User.query.filter(User.id.in_(ids)).all()
        for user in users:
            user.status = 0
            db.session.commit()
        return jsonify(ids)
    return jsonify("Не выбраны записи")

#Форма добавления нового пользователя
@app.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    current_user = get_current_user()

    form_user_add = AddUserForm()
    users_all_count = User.query.count()

    if form_user_add.validate_on_submit():
        if request.method  == 'POST':
            login = form_user_add.login.data
            password = form_user_add.password.data
            surname = form_user_add.surname.data
            name= form_user_add.name.data
            patronymic = form_user_add.patronymic.data
            email = form_user_add.email.data
            phone = form_user_add.phone.data
            birth_date = form_user_add.birth_date.data
            work_date = form_user_add.work_date.data
            department_id = form_user_add.department_id.data
            post_id = form_user_add.post_id.data
            role_id = form_user_add.role_id.data

            print login
            print password
            print surname
            print name
            print patronymic
            print email
            print phone
            print birth_date
            print work_date
            print department_id
            print post_id
            print role_id
            #~ if form_user_add.user.data:
            #~ user = User(
            #~ login = form_user_add.login.data,
            #~ password = form_user_add.password.data,
            #~ surname = form_user_add.surname.data,
            #~ name= form_user_add.name.data,
            #~ patronymic = form_user_add.patronymic.data,
            #~ email = form_user_add.email.data,
            #~ phone = form_user_add.phone.data,
            #~ birth_date = form_user_add.birth_date.data
            #~ )
            #~ db.session.add(user)
            #~ db.session.commit()
            flash(u"Пользователь добавлен", 'success')
            return redirect(url_for('admin_users'))
    return render_template("admin/add_users.html", form_user_add = form_user_add, users_all_count = users_all_count, current_user=current_user)
