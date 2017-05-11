#! venv/bin/python

from app import app, db
from models import User, Department, Role, Post, Important_news, Table, History
from forms import LoginForm, DelUserForm, AddUserForm, EditUserForm, AddRoleForm, DelRoleForm, AddDepartmentForm, DelDepartmentForm, AddPostForm, DelPostForm, DelImportantForm
from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response
from functools import wraps
from config import basedir, PER_PAGE, SQLALCHEMY_DATABASE_URI, AVATARS_FOLDER
from flask_paginate import Pagination
from sqlalchemy import create_engine
import time, calendar, os, hashlib, shutil, uuid, json, datetime

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

#Добавление в историю
def make_history(str_table, str_action, current_user_id):
    table_id = Table.query.filter(Table.url == str_table).first()
    action = History(user_id=current_user_id, action = str_action, table = table_id.id)
    db.session.add(action)
    return "success"

#Счетчики
def get_counters():
    user_count = User.query.count()
    role_count = Role.query.count()
    department_count = Department.query.count()
    post_count = Post.query.count()
    counters_dict={}
    for name in ['user_count','role_count','department_count','post_count']:
        counters_dict.update({name:eval(name)})
    return counters_dict

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
    all_counters = get_counters()
    birth_celebrate = {}
    worktime_celebrate = {}
    today = time.strftime("%Y-%m-%d")

    important_news_all = Important_news.query.all()
    for news in important_news_all:
        if ((news.expired is not None) and (datetime.datetime.now() >= news.expired)):
            Important_news.query.filter(Important_news.id == news.id).delete()
            db.session.commit()
            important_news_all = Important_news.query.all()

    for user in users_all:
        if user.birth_date.month ==  int(time.strftime("%m")):
            birth_celebrate.update({'%s %s %s'%(user.surname, user.name, user.patronymic):[user.birth_date.day, user.post.id]})
        if user.work_date.month ==  int(time.strftime("%m")):
            worktime_celebrate.update({'%s %s %s'%(user.surname, user.name, user.patronymic):[user.work_date.day, user.post.id]})

    form_delete = DelImportantForm()

    if form_delete.validate_on_submit():
        important_id = form_delete.del_id.data
        Important_news.query.filter(Important_news.id == important_id).delete()
        make_history("important", "удаление", current_user.id)
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template("admin/admin.html",  current_user=current_user, last_login=session['last_login'], time_worked = time_worked, birth_celebrate=birth_celebrate,
    worktime_celebrate=worktime_celebrate, today=today, all_counters=all_counters, important_news_all=important_news_all, form_delete=form_delete)

#Быстрое изменение данных записи
@app.route('/fast_important_edit', methods = ['POST'])
def fast_important_edit():
    current_user = get_current_user()
    request_data = request.form
    edit_data= Important_news.query.get(request_data['pk'])
    if request.method  == 'POST':
        if request_data['name'] == 'text':
            edit_data.text = request_data['value']
        else:
            if request_data['value']:
                edit_data.expired = request_data['value']
            else:
                edit_data.expired = None
        make_history("important", "редактирование", current_user.id)
        db.session.commit()
    response = app.response_class(
        response=json.dumps({"Успешно изменено!":edit_data.id}),
        status=200,
        mimetype='application/json'
    )
    return response

#Добавление важной новости
@app.route('/new_important', methods = ['POST'])
def new_important():
    request_data = request.form
    current_user = get_current_user()
    if request.method  == 'POST':
        data = Important_news(text=request_data['value'], author = current_user.id, expired=datetime.datetime.now()+datetime.timedelta(days=30))
        db.session.add(data)
        make_history("important", "вставку", current_user.id)
        db.session.commit()
    destination = url_for('admin')
    response = Response(
        response=json.dumps({'url':destination,'plus':'<i class="fa fa-plus fa-control" aria-hidden="true"></i>'}),
        status=200,
        mimetype='application/json'
    )
    return response

#Страница со списком пользователей
@app.route('/admin/users', methods=['GET', 'POST'])
@app.route('/admin/users/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_users(page = 1, *args):

    current_user = get_current_user()
    if current_user.role.id != 1:
        return forbidden(403)

    users_all = User.query.order_by(User.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('user_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelUserForm()

    if form_delete.validate_on_submit():
        user_id = form_delete.del_id.data
        User.query.filter(User.id == user_id).delete()
        make_history("users", "удаление", current_user.id)
        db.session.commit()
        flash(u"Пользователь удален", 'success')
        return redirect(url_for('admin_users', page = page))

    return render_template("admin/list_users.html", users_all = users_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today,
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
    current_user = get_current_user()
    ids = request.form.getlist('param[]')
    table = request.form.getlist('table')
    if ids:
        if table[0] == 'user':
            users = User.query.filter(User.id.in_(ids)).all()
            for user in users:
                db.session.delete(user)
            make_history("users", "удаление", current_user.id)
        if table[0] == 'role':
            roles = Role.query.filter(Role.id.in_(ids)).all()
            for role in roles:
                db.session.delete(role)
            make_history("roles", "удаление", current_user.id)
        if table[0] == 'department':
            departments = Department.query.filter(Department.id.in_(ids)).all()
            for department in departments:
                db.session.delete(department)
            make_history("departments", "удаление", current_user.id)
        if table[0] == 'post':
            posts = Post.query.filter(Post.id.in_(ids)).all()
            for post in posts:
                db.session.delete(post)
            make_history("posts", "удаление", current_user.id)
        db.session.commit()
        return jsonify(ids)
    return jsonify("Не выбраны записи")

#Отлючение нескольких записей
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
    today = time.strftime("%Y-%m-%d")

    form_user_add = AddUserForm()
    all_counters = get_counters()

    if form_user_add.validate_on_submit():
        if request.method  == 'POST':

            print form_user_add.role_id.data
            photo = request.files['photo']
            if photo:
                hashname = uuid.uuid4().hex + '.' + photo.filename.rsplit('.', 1)[1]
                photo.save(os.path.join(app.config['AVATARS_FOLDER'], hashname))
            else:
                hashname = None

            check = User.query.filter((User.login==form_user_add.login.data)|(User.email==form_user_add.email.data)|(User.phone==form_user_add.phone.data)).first()

            if check:
                flash(u"Уже существует пользователь с таким логином, почтой или телефоном", 'error')
            else:
                user = User(
                login = form_user_add.login.data,
                password = hashlib.md5(form_user_add.password.data.encode('utf-8')).hexdigest(),
                surname = form_user_add.surname.data,
                name= form_user_add.name.data,
                patronymic = form_user_add.patronymic.data,
                email = form_user_add.email.data,
                phone = form_user_add.phone.data,
                birth_date = form_user_add.birth_date.data,
                work_date = form_user_add.work_date.data,
                status = 1,
                department_id = form_user_add.department_id.data.id,
                post_id = form_user_add.post_id.data.id,
                role_id = form_user_add.role_id.data.id,
                photo = hashname )

                db.session.add(user)
                make_history("users", "вставку", current_user.id)
                db.session.commit()

                flash(u"Пользователь добавлен", 'success')
                return redirect(url_for('admin_users'))
    return render_template("admin/add_users.html", form_user_add = form_user_add, all_counters = all_counters, current_user=current_user, today=today)

#Форма изменения пользователя
@app.route('/admin/users/edit', methods=['GET', 'POST'])
@login_required
def edit_user():
    current_user = get_current_user()
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")

    edit_user = User.query.get(request.args.get('id'))

    form_user_edit = EditUserForm(
    name=edit_user.name,
    login=edit_user.login,
    email=edit_user.email,
    phone=edit_user.phone,
    surname=edit_user.surname,
    patronymic=edit_user.patronymic,
    birth_date=edit_user.birth_date,
    work_date=edit_user.work_date,
    status=edit_user.status,
    department_id=edit_user.department_id,
    post_id=edit_user.post_id,
    role_id=edit_user.role_id
    )

    if form_user_edit.validate_on_submit():
        if request.method  == 'POST':

            login = form_user_edit.login.data
            password = form_user_edit.password.data
            email = form_user_edit.email.data
            phone = form_user_edit.phone.data
            error = False

            if password:
                password = hashlib.md5(form_user_edit.password.data.encode('utf-8')).hexdigest()
            else:
                password = edit_user.password

            if login:
                check = User.query.filter(User.login==login).first()
                if (check and (check.id!=edit_user.id)):
                    error = True
                    form_user_edit.login.errors.append('Пользователь с такими данными существует')

            if email:
                check = User.query.filter(User.email==email).first()
                if (check and (check.id!=edit_user.id)):
                    error = True
                    form_user_edit.email.errors.append('Пользователь с такими данными существует')

            if phone:
                check = User.query.filter(User.phone==phone).first()
                if (check and (check.id!=edit_user.id)):
                    error = True
                    form_user_edit.phone.errors.append('Пользователь с такими данными существует')

            if error:
                flash(u"Уже существует пользователь с таким логином, почтой или телефоном", 'error')
            else:
                photo = request.files['photo']
                if photo:
                    hashname = uuid.uuid4().hex + '.' + photo.filename.rsplit('.', 1)[1]
                    photo.save(os.path.join(app.config['AVATARS_FOLDER'], hashname))
                else:
                    hashname = edit_user.photo

                edit_user.login = login
                edit_user.password = password
                edit_user.surname = form_user_edit.surname.data
                edit_user.name= form_user_edit.name.data
                edit_user.patronymic = form_user_edit.patronymic.data
                edit_user.email = email
                edit_user.phone = phone
                edit_user.birth_date = form_user_edit.birth_date.data
                edit_user.work_date = form_user_edit.work_date.data
                edit_user.status = form_user_edit.status.data
                edit_user.department_id = form_user_edit.department_id.data
                edit_user.post_id = form_user_edit.post_id.data
                edit_user.role_id = form_user_edit.role_id.data
                edit_user.photo = hashname

                make_history("users", "редактирование", current_user.id)
                db.session.commit()

                flash(u"Пользователь изменен", 'success')
                return redirect(url_for('admin_users'))
    return render_template("admin/edit_users.html", form_user_edit = form_user_edit, all_counters = all_counters, current_user=current_user, today=today)

#Быстрое изменение данных записи
@app.route('/post', methods = ['POST'])
def get_post_user():
    request_user = request.form
    #~ print request.form
    #~ print request.form['name']
    #~ print request_user['pk']
    #~ print request_user['value']
    edit_user = User.query.get(request_user['pk'])
    if request_user['name'] == 'role':
        edit_user.role_id = int(request_user['value'])
    if request_user['name'] == 'department':
        edit_user.department_id = int(request_user['value'])
    if request_user['name'] == 'post':
        edit_user.post_id = int(request_user['value'])
    db.session.commit()
    return jsonify(u'Успешно')

#Получение данных из таблицы и возвращение json в javascript
@app.route('/get', methods = ['GET'])
def get_bootstap_editable():
    posts = Post.query.all()
    Posts_list ={}
    for post in posts:
        Posts_list.update({str(post.id):post.name})
    departments = Department.query.all()
    Departments_list ={}
    for department in departments:
        Departments_list.update({str(department.id):department.name})
    roles = Role.query.all()
    Roles_list ={}
    for role in roles:
        Roles_list.update({str(role.id):role.name})
    return jsonify(Posts_list, Departments_list, Roles_list)

#Страница со списком ролей
@app.route('/admin/roles', methods=['GET', 'POST'])
@app.route('/admin/roles/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_roles(page = 1, *args):

    current_user = get_current_user()
    if current_user.role.id != 1:
        return forbidden(403)

    roles_all = Role.query.order_by(Role.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('role_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelRoleForm()

    if form_delete.validate_on_submit():
        role_id = form_delete.del_id.data
        Role.query.filter(Role.id == role_id).delete()
        make_history("roles", "удаление", current_user.id)
        db.session.commit()
        flash(u"Роль удалена", 'success')
        return redirect(url_for('admin_roles', page = page))

    return render_template("admin/list_roles.html", roles_all = roles_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, form_delete=form_delete)

#Быстрое изменение данных записи
@app.route('/fast_role_edit', methods = ['POST'])
def fast_role_edit():
    current_user = get_current_user()
    request_user = request.form
    edit_role = Role.query.get(request_user['pk'])
    if request.method  == 'POST':
        edit_role.name = request_user['value']
        make_history("roles", "редактирование", current_user.id)
        db.session.commit()
    response = app.response_class(
        response=json.dumps({"Успешно изменено!":edit_role.id}),
        status=200,
        mimetype='application/json'
    )
    return response

#Форма добавления новой роли
@app.route('/admin/roles/new', methods=['GET', 'POST'])
@login_required
def new_role():
    current_user = get_current_user()
    today = time.strftime("%Y-%m-%d")

    form_role_add = AddRoleForm()
    all_counters = get_counters()

    if form_role_add.validate_on_submit():
        if request.method  == 'POST':
            role = Role(name = form_role_add.name.data)
            db.session.add(role)
            make_history("roles", "вставку", current_user.id)
            db.session.commit()

            flash(u"Роль добавлена", 'success')
            return redirect(url_for('admin_roles'))
    return render_template("admin/add_roles.html", form_role_add = form_role_add, all_counters = all_counters, current_user=current_user, today=today)

#Страница со списком отделов
@app.route('/admin/departments', methods=['GET', 'POST'])
@app.route('/admin/departments/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_departments(page = 1, *args):

    current_user = get_current_user()
    if current_user.role.id != 1:
        return forbidden(403)

    departments_all = Department.query.order_by(Department.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('department_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelDepartmentForm()

    if form_delete.validate_on_submit():
        department_id = form_delete.del_id.data
        Department.query.filter(Department.id == department_id).delete()
        make_history("departments", "удаление", current_user.id)
        db.session.commit()
        flash(u"Отдел удален", 'success')
        return redirect(url_for('admin_departments', page = page))

    return render_template("admin/list_departments.html", departments_all = departments_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, form_delete=form_delete)

#Быстрое изменение данных записи
@app.route('/fast_department_edit', methods = ['POST'])
def fast_department_edit():
    current_user = get_current_user()
    request_user = request.form
    edit_department = Department.query.get(request_user['pk'])
    if request.method  == 'POST':
        edit_department.name = request_user['value']
        make_history("departments", "редактирование", current_user.id)
        db.session.commit()
    response = app.response_class(
        response=json.dumps({u'Успешно изменено!':edit_department.id}),
        status=200,
        mimetype='application/json'
    )
    return response

#Форма добавления нового отдела
@app.route('/admin/departments/new', methods=['GET', 'POST'])
@login_required
def new_department():
    current_user = get_current_user()
    today = time.strftime("%Y-%m-%d")

    form_department_add = AddDepartmentForm()
    all_counters = get_counters()

    if form_department_add.validate_on_submit():
        if request.method  == 'POST':
            department = Department(name = form_department_add.name.data)
            db.session.add(department)
            make_history("departments", "вставку", current_user.id)
            db.session.commit()

            flash(u"Отдел добавлен", 'success')
            return redirect(url_for('admin_departments'))
    return render_template("admin/add_departments.html", form_department_add = form_department_add, all_counters = all_counters, current_user=current_user, today=today)

#Страница со списком должностей
@app.route('/admin/posts', methods=['GET', 'POST'])
@app.route('/admin/posts/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_posts(page = 1, *args):

    current_user = get_current_user()
    if current_user.role.id != 1:
        return forbidden(403)

    posts_all = Post.query.order_by(Post.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('post_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelPostForm()

    if form_delete.validate_on_submit():
        post_id = form_delete.del_id.data
        Post.query.filter(Post.id == post_id).delete()
        make_history("posts", "удаление", current_user.id)
        db.session.commit()
        flash(u"Должность удалена", 'success')
        return redirect(url_for('admin_posts', page = page))

    return render_template("admin/list_posts.html", posts_all = posts_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, form_delete=form_delete)

#Быстрое изменение данных записи
@app.route('/fast_post_edit', methods = ['POST'])
def fast_post_edit():
    current_user = get_current_user()
    request_post = request.form
    edit_post = Post.query.get(request_post['pk'])
    if request.method  == 'POST':
        edit_post.name = request_post['value']
        make_history("posts", "редактирование", current_user.id)
        db.session.commit()
    response = app.response_class(
        response=json.dumps({u'Успешно изменено!':edit_post.id}),
        status=200,
        mimetype='application/json'
    )
    return response

#Форма добавления нового должности
@app.route('/admin/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    current_user = get_current_user()
    today = time.strftime("%Y-%m-%d")

    form_posts_add = AddPostForm()
    all_counters = get_counters()

    if form_posts_add.validate_on_submit():
        if request.method  == 'POST':
            post = Post(name = form_posts_add.name.data)
            db.session.add(post)
            make_history("posts", "вставку", current_user.id)
            db.session.commit()

            flash(u"Должность добавлена", 'success')
            return redirect(url_for('admin_posts'))
    return render_template("admin/add_posts.html", form_posts_add = form_posts_add, all_counters = all_counters, current_user=current_user, today=today)

#Страница с историей действий
@app.route('/admin/history', methods=['GET', 'POST'])
@app.route('/admin/history/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_history(page = 1, *args):

    current_user = get_current_user()
    all_counters = get_counters()

    actions_all = History.query.filter(History.user_id == current_user.id).order_by(History.id.desc())
    all_count = actions_all.count()
    actions_all = actions_all.paginate(page, 100, False)

    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_count, per_page = 100, css_framework='bootstrap3')

    return render_template("admin/list_history.html", actions_all = actions_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today)

#Страница с историей действий всех пользователей
@app.route('/admin/history/all', methods=['GET', 'POST'])
@app.route('/admin/history/all/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_history_all(page = 1, *args):

    current_user = get_current_user()
    if current_user.role.id != 1:
        return forbidden(403)

    all_counters = get_counters()

    actions_all = History.query.order_by(History.id.desc()).paginate(page, 100, False)
    all_count = History.query.count()

    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_count, per_page = 100, css_framework='bootstrap3')

    return render_template("admin/list_history.html", actions_all = actions_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today)
