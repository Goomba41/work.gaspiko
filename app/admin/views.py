#! venv/bin/python

from app import app, db

from app.authentication.views import login_required

from app.models import User, Department, Role, Post, Important_news, Table_db, History, Permission, Module, News, Appeals, Executor, Request
from app.admin.forms import DelUserForm, AddUserForm, EditUserForm, AddRoleForm, DelRoleForm, AddDepartmentForm, DelDepartmentForm, AddPostForm, DelPostForm, DelImportantForm, DelPermissionForm, AddPermissionForm, DelNewsForm, AddNewsForm, EditNewsForm

from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response, Blueprint
from functools import wraps
from config import basedir, PER_PAGE, SQLALCHEMY_DATABASE_URI, AVATARS_FOLDER, REQUEST_FILES_FOLDER
from flask_paginate import Pagination
from sqlalchemy import create_engine
from sqlalchemy.sql.functions import func
import time, calendar, os, hashlib, shutil, uuid, json, datetime, inspect, ast, redis
from flask_sse import sse
from collections import defaultdict

from sqlalchemy import *

administration = Blueprint('admin', __name__, url_prefix='/admin')

#Функция обработки склонений
def get_com(x, y):
    inumber = x % 100
    if inumber >= 11 and inumber <=19:
        y = y[2]
    else:
        iinumber = inumber % 10
        if iinumber == 1:
            y = y[0]
        elif iinumber == 2 or iinumber == 3 or iinumber == 4:
            y = y[1]
        else:
            y = y[2]
    return (x,y)

#Функция счета стажа
#~ @app.template_filter('standing')
@administration.context_processor
def standing():
    def _standing(f, begin_year):
        now = str(time.strftime("%Y-%m-%d"))
        first = str(f)
        now = now.split('-')
        first = first.split('-')

        if begin_year:
            date_first = (int(now[0]),int(1),int(1))
        else:
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

        time_worked = [
        get_com(date_result[0], [u"год", u"года", u"лет"]),
        get_com(date_result[1], [u"месяц", u"месяца", u"месяцев"]),
        get_com(date_result[2],  [u"день", u"дня", u"дней"])]

        return time_worked
    return dict(standing=_standing)

#Текущий пользователь
def get_current_user():
    current_user = User.query.filter(User.id == session['user_id']).first()
    return current_user

#Разрешения пользователя
def get_permissions(role_id, user_id, url, operation):

    table_id = Table_db.query.filter(Table_db.url == url).first().id
    perm= Permission.query.filter(((Permission.role_id==role_id)|(Permission.user_id==user_id))&(Permission.table_id == table_id)).all()

    list = []
    temp = False

    if operation == "enter":
        for p in perm:
            #~ print p, p.enter
            list.append(p.enter)
    if operation == "insert":
        for p in perm:
            #~ print p, p.insert
            list.append(p.insert)
    if operation == "update":
        for p in perm:
            #~ print p, p.update
            list.append(p.update)
    if operation == "delete":
        for p in perm:
            #~ print p, p.delete
            list.append(p.delete)

    for l in list:
        temp = temp or l

    return temp

#Добавление в историю
def make_history(str_table, str_action, current_user_id):
    table_id = Table_db.query.filter(Table_db.url == str_table).first()
    action = History(user_id=current_user_id, action = str_action, table = table_id.id)
    db.session.add(action)
    return "success"

#Счетчики
def get_counters():
    user_count = User.query.count()
    role_count = Role.query.count()
    department_count = Department.query.count()
    post_count = Post.query.count()
    news_count = News.query.count()
    appeals_count_all = Appeals.query.count()
    appeals_count_done = Appeals.query.filter((Appeals.status==3)|(Appeals.status==5)).count()
    appeals_count_new = Appeals.query.filter(Appeals.status==1).count()
    appeals_count_checked = Appeals.query.filter(Appeals.status==5).count()
    counters_dict={}
    for name in ['user_count','role_count','department_count','post_count','news_count', 'appeals_count_all', 'appeals_count_done', 'appeals_count_new','appeals_count_checked']:
        counters_dict.update({name:eval(name)})
    return counters_dict

#Фильтр для шаблона рута admin для разделения даты, получаемой из ключа словаря в виде строки (праздники)
@app.template_filter('date')
def get_date(date):
    date = datetime.datetime.strptime(date, '%m-%d')
    return date.month, date.day

#Обработчик ошибки 403 - доступ запрещен
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

#Админка основной экран
@administration.route('/', methods=['GET', 'POST'])
@login_required
def admin():
    current_user = get_current_user()

    permissions = Permission.query.filter(((Permission.user_id == current_user.id)&(Permission.enter == 1))|((Permission.role_id == current_user.role.id)&(Permission.enter == 1))).all()

    url = 'important'
    delete = get_permissions(current_user.role.id, current_user.id, url, "delete")
    print ("delete "+str(delete))

    #~ time_worked = standing(current_user.work_date)
    time_worked = standing().get('standing')
    time_worked = time_worked(current_user.work_date, False)

    users_all = User.query.all()
    all_counters = get_counters()
    birth_celebrate = {}
    #~ worktime_celebrate = {}
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
        #~ if user.work_date.month ==  int(time.strftime("%m")):
            #~ worktime_celebrate.update({'%s %s %s'%(user.surname, user.name, user.patronymic):[user.work_date.day, user.post.id]})

    with open(os.path.join(basedir, 'app/static/admin/celebration'), 'r') as jsonfile:
        celebration = json.load(jsonfile)

    form_delete = DelImportantForm()

    if form_delete.validate_on_submit() and delete:
            important_id = form_delete.del_id.data
            Important_news.query.filter(Important_news.id == important_id).delete()
            make_history("important", "удаление", current_user.id)
            db.session.commit()
            return redirect(url_for('admin.admin'))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin'))

    # Попытка сделать напоминание за день до дня рождения пользователя: проблема - как запомнить что сообщение уже отработало
    #~ if request.cookies.get('reminder_birthday'):
        #~ reminder_birthday_state = request.cookies.get('reminder_birthday')
    #~ else:
        #~ reminder_birthday_state =  'off'
    #~ if reminder_birthday_state == 'on':
        #~ birth_celebrate_wth_nxt_mnt = dict(birth_celebrate)
        #~ for user in users_all:
            #~ if user.birth_date.month ==  int(time.strftime("%m"))+1:
                #~ birth_celebrate_wth_nxt_mnt.update({'%s %s %s'%(user.surname, user.name, user.patronymic):[user.birth_date.day, user.id]})
        #~ days = calendar.monthrange(int(time.strftime("%Y")), int(time.strftime("%m")))
        #~ tmp_d =  int(time.strftime("%m")) + 1
        #~ if tmp_d > days[1]:
            #~ tmp_d = 1
        #~ for key, value in birth_celebrate_wth_nxt_mnt.iteritems():
            #~ if value[0] ==  tmp_d:
                #~ congrats = "У пользователя " + str(key.encode('utf-8')+" завтра день рождения, не забудьте поздравить!")
                #~ sse.publish({"message": congrats, "exclude":value[1], "retry":30000}, type='birthday', retry=30)
                #~ sse.publish({"message": "У пользователя %s завтра день рождения, не забудьте поздравить!"%(key.encode('utf-8')), "exclude":value[1], "retry":30000}, type='birthday', retry=30)

    return render_template("admin/admin.html",  current_user=current_user, permissions = permissions, last_login=session['last_login'], time_worked = time_worked, birth_celebrate=birth_celebrate,
    today=today, all_counters=all_counters, important_news_all=important_news_all, form_delete=form_delete, celebration=celebration)

#Быстрое изменение данных записи
@administration.route('/fast_important_edit', methods = ['POST'])
def fast_important_edit():
    current_user = get_current_user()

    url = 'important'
    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
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
    else:
        flash(u"Вам запрещено данное действие", 'error')
        response = app.response_class(
            response=json.dumps({"Вам запрещено данное действие!":0}),
            status=200,
            mimetype='application/json'
        )
    return response

#Добавление важной новости
@administration.route('/new_important', methods = ['POST'])
def new_important():
    current_user = get_current_user()

    url = 'important'
    insert = get_permissions(current_user.role.id, current_user.id, url, "insert")
    print ("insert "+str(insert))

    if insert:
        request_data = request.form
        if request.method  == 'POST':
            data = Important_news(text=request_data['value'], author = current_user.id, expired=datetime.datetime.now()+datetime.timedelta(days=30))
            db.session.add(data)
            make_history("important", "вставку", current_user.id)
            db.session.commit()
        destination = url_for('admin.admin')
        response = Response(
            response=json.dumps({'url':destination,'plus':'<i class="fa fa-plus fa-control" aria-hidden="true"></i>'}),
            status=200,
            mimetype='application/json'
        )
    else:
        flash(u"Вам запрещено данное действие", 'error')
        response = app.response_class(
            response=json.dumps({"Вам запрещено данное действие!":0}),
            status=200,
            mimetype='application/json'
        )
    return response

#Страница со списком пользователей
@administration.route('/users', methods=['GET', 'POST'])
@administration.route('/users/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_users(page = 1, *args):

    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "users", "enter")
    print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    users_all = User.query.order_by(User.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('user_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelUserForm()
    delete = get_permissions(current_user.role.id, current_user.id, "users", "delete")
    print ("delete "+str(delete))

    if form_delete.validate_on_submit() and delete:
        user_id = form_delete.del_id.data
        user = User.query.filter(User.id == user_id).first()
        make_history("users", "удаление", current_user.id)
        if user.photo:
            os.remove(os.path.join(app.config['AVATARS_FOLDER'], user.photo))
        db.session.delete(user)
        db.session.commit()
        flash(u"Пользователь удален", 'success')
        return redirect(url_for('admin.admin_users', page = page))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin_users', page = page))

    return render_template("admin/list_users.html", users_all = users_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today,
     form_delete=form_delete)

#Сброс и установка нового пароля для пользователя
@administration.route('/password_reset', methods = ['POST'])
def get_post_javascript_data_password():
    current_user = get_current_user()
    url = 'users'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
        new_password = request.form['new_password']
        user = request.form['user']

        user_change = User.query.filter(User.id == user).first()
        password_hash = hashlib.md5(new_password).hexdigest()
        user_change.password = password_hash
        db.session.commit()

        return jsonify("Успешно")
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Удаление нескольких записей
@administration.route('/rows_delete', methods = ['POST'])
def get_post_javascript_data_id_delete():
    current_user = get_current_user()

    ids = request.form.getlist('param[]')
    table = request.form.getlist('table')
    if ids:
        url = table[0]
        delete = get_permissions(current_user.role.id, current_user.id, url, "delete")
        print ("delete "+str(delete))
        if delete:
            if table[0] == 'users':
                users = User.query.filter(User.id.in_(ids)).all()
                for user in users:
                    db.session.delete(user)
                    os.remove(os.path.join(app.config['AVATARS_FOLDER'], user.photo))
                make_history("users", "удаление", current_user.id)
            if table[0] == 'roles':
                roles = Role.query.filter(Role.id.in_(ids)).all()
                for role in roles:
                    db.session.delete(role)
                make_history("roles", "удаление", current_user.id)
            if table[0] == 'departments':
                departments = Department.query.filter(Department.id.in_(ids)).all()
                for department in departments:
                    db.session.delete(department)
                make_history("departments", "удаление", current_user.id)
            if table[0] == 'posts':
                posts = Post.query.filter(Post.id.in_(ids)).all()
                for post in posts:
                    db.session.delete(post)
                make_history("posts", "удаление", current_user.id)
            if table[0] == 'news':
                news = News.query.filter(News.id.in_(ids)).all()
                for new in news:
                    db.session.delete(new)
                    os.remove(os.path.join(app.config['COVERS_FOLDER'], new.cover))
                make_history("news", "удаление", current_user.id)
            if table[0] == 'executors':
                executors = Executor.query.filter(Executor.id.in_(ids)).all()
                for executor in executors:
                    db.session.delete(executor)
                make_history("executors", "удаление", current_user.id)
            if table[0] == 'requests':
                requests = Request.query.filter(Request.id.in_(ids)).all()
                for request_d in requests:
                    db.session.delete(request_d)
                    if request_d.filename:
                        os.remove(os.path.join(REQUEST_FILES_FOLDER, request_d.filename))
                make_history("requests", "удаление", current_user.id)
            db.session.commit()
            flash(u"Записи удалены", 'success')
            return jsonify(ids)
        else:
            flash(u"Вам запрещено данное действие", 'error')
            return jsonify("Запрещено данное действие")
    flash(u"Не выбраны записи", 'error')
    return jsonify("Не выбраны записи")

#Отлючение нескольких записей
@administration.route('/rows_disable', methods = ['POST'])
def get_post_javascript_data_id_disable():
    current_user = get_current_user()
    url = 'users'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
        ids = request.form.getlist('param[]')
        if ids:
            users = User.query.filter(User.id.in_(ids)).all()
            for user in users:
                user.status = 0
                db.session.commit()
            return jsonify(ids)
        return jsonify("Не выбраны записи")
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Отлючение одной записи
@administration.route('/user_disable', methods = ['POST'])
def user_disable():
    current_user = get_current_user()
    url = 'users'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
        id = request.json
        if id:
            user = User.query.filter(User.id==id).first()
            if user.status == 0:
                user.status = 1
            else:
                user.status = 0
            db.session.commit()
            return jsonify("Успешно изменена запись")
        return jsonify("Непредвиденная ошибка")
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Форма добавления нового пользователя
@administration.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "users", "enter")
    print ("enter "+str(enter))
    insert = get_permissions(current_user.role.id, current_user.id, "users", "insert")
    print ("insert "+str(insert))

    if not enter or not insert:
        return forbidden(403)

    today = time.strftime("%Y-%m-%d")

    form_user_add = AddUserForm()
    all_counters = get_counters()

    if form_user_add.validate_on_submit():
        if request.method  == 'POST':

            print (form_user_add.role_id.data)
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
                return redirect(url_for('admin.admin_users'))
    return render_template("admin/add_users.html", form_user_add = form_user_add, all_counters = all_counters, current_user=current_user, today=today)

#Форма изменения пользователя
@administration.route('/users/edit', methods=['GET', 'POST'])
@login_required
def edit_user():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "users", "enter")
    print ("enter "+str(enter))
    update = get_permissions(current_user.role.id, current_user.id, "users", "update")
    print ("update "+str(update))

    if not enter or not update:
        return forbidden(403)

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
                    if edit_user.photo is not None:
                        photo.save(os.path.join(app.config['AVATARS_FOLDER'], edit_user.photo))
                    else:
                        hashname = uuid.uuid4().hex + '.' + photo.filename.rsplit('.', 1)[1]
                        photo.save(os.path.join(app.config['AVATARS_FOLDER'], hashname))
                        edit_user.photo = hashname

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


                make_history("users", "редактирование", current_user.id)
                db.session.commit()

                flash(u"Пользователь изменен", 'success')
                return redirect(url_for('admin.admin_users'))
    return render_template("admin/edit_users.html", form_user_edit = form_user_edit, all_counters = all_counters, current_user=current_user, today=today)

#Быстрое изменение данных записи
@administration.route('/post', methods = ['POST'])
def get_post_user():
    current_user = get_current_user()
    url = 'users'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
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
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Получение данных из таблицы и возвращение json в javascript для составления списков в выпадающих списках
@administration.route('/get', methods = ['GET'])
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
@administration.route('/roles', methods=['GET', 'POST'])
@administration.route('/roles/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_roles(page = 1, *args):

    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "roles", "enter")
    delete = get_permissions(current_user.role.id, current_user.id, "roles", "delete")
    print ("enter "+str(enter))
    print ("delete "+str(delete))

    if not enter:
        return forbidden(403)

    roles_all = Role.query.order_by(Role.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('role_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelRoleForm()

    if form_delete.validate_on_submit() and delete:
        role_id = form_delete.del_id.data
        Role.query.filter(Role.id == role_id).delete()
        make_history("roles", "удаление", current_user.id)
        db.session.commit()
        flash(u"Роль удалена", 'success')
        return redirect(url_for('admin.admin_roles', page = page))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin_roles', page = page))

    return render_template("admin/list_roles.html", roles_all = roles_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, form_delete=form_delete)

#Быстрое изменение данных записи
@administration.route('/fast_role_edit', methods = ['POST'])
def fast_role_edit():
    current_user = get_current_user()
    url = 'roles'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
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
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Форма добавления новой роли
@administration.route('/roles/new', methods=['GET', 'POST'])
@login_required
def new_role():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "roles", "enter")
    print ("enter "+str(enter))
    insert = get_permissions(current_user.role.id, current_user.id, "roles", "insert")
    print ("insert "+str(insert))

    if not enter or not insert:
        return forbidden(403)

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
            return redirect(url_for('admin.admin_roles'))
    return render_template("admin/add_roles.html", form_role_add = form_role_add, all_counters = all_counters, current_user=current_user, today=today)

#Страница со списком отделов
@administration.route('/departments', methods=['GET', 'POST'])
@administration.route('/departments/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_departments(page = 1, *args):
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "departments", "enter")
    delete = get_permissions(current_user.role.id, current_user.id, "departments", "delete")
    print ("enter "+str(enter))
    print ("delete "+str(delete))

    if not enter:
        return forbidden(403)

    departments_all = Department.query.order_by(Department.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('department_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelDepartmentForm()

    if form_delete.validate_on_submit() and delete:
        department_id = form_delete.del_id.data
        Department.query.filter(Department.id == department_id).delete()
        make_history("departments", "удаление", current_user.id)
        db.session.commit()
        flash(u"Отдел удален", 'success')
        return redirect(url_for('admin.admin_departments', page = page))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin_departments', page = page))

    return render_template("admin/list_departments.html", departments_all = departments_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, form_delete=form_delete)

#Быстрое изменение данных записи
@administration.route('/fast_department_edit', methods = ['POST'])
def fast_department_edit():
    current_user = get_current_user()
    url = 'departments'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
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
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Форма добавления нового отдела
@administration.route('/departments/new', methods=['GET', 'POST'])
@login_required
def new_department():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "departments", "enter")
    print ("enter "+str(enter))
    insert = get_permissions(current_user.role.id, current_user.id, "departments", "insert")
    print ("insert "+str(insert))

    if not enter or not insert:
        return forbidden(403)

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
            return redirect(url_for('admin.admin_departments'))
    return render_template("admin/add_departments.html", form_department_add = form_department_add, all_counters = all_counters, current_user=current_user, today=today)

#Страница со списком должностей
@administration.route('/posts', methods=['GET', 'POST'])
@administration.route('/posts/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_posts(page = 1, *args):
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "posts", "enter")
    delete = get_permissions(current_user.role.id, current_user.id, "posts", "delete")
    print ("enter "+str(enter))
    print ("delete "+str(delete))

    if not enter:
        return forbidden(403)

    posts_all = Post.query.order_by(Post.id.asc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('post_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelPostForm()

    if form_delete.validate_on_submit() and delete:
        post_id = form_delete.del_id.data
        Post.query.filter(Post.id == post_id).delete()
        make_history("posts", "удаление", current_user.id)
        db.session.commit()
        flash(u"Должность удалена", 'success')
        return redirect(url_for('admin.admin_posts', page = page))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin_posts', page = page))

    return render_template("admin/list_posts.html", posts_all = posts_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, form_delete=form_delete)

#Быстрое изменение данных записи
@administration.route('/fast_post_edit', methods = ['POST'])
def fast_post_edit():
    current_user = get_current_user()
    url = 'posts'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
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
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Форма добавления нового должности
@administration.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "posts", "enter")
    print ("enter "+str(enter))
    insert = get_permissions(current_user.role.id, current_user.id, "posts", "insert")
    print ("insert "+str(insert))

    if not enter or not insert:
        return forbidden(403)

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
            return redirect(url_for('admin.admin_posts'))
    return render_template("admin/add_posts.html", form_posts_add = form_posts_add, all_counters = all_counters, current_user=current_user, today=today)

#Страница с историей действий
@administration.route('/history', methods=['GET', 'POST'])
@administration.route('/history/<int:page>', methods=['GET', 'POST'])
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
@administration.route('/history/all', methods=['GET', 'POST'])
@administration.route('/history/all/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_history_all(page = 1, *args):

    current_user = get_current_user()

    all_counters = get_counters()

    actions_all = History.query.order_by(History.id.desc()).paginate(page, 100, False)
    all_count = History.query.count()

    count_table_uses = History.query.with_entities(History.table, Table_db.name, Module.name,func.count(History.table).label('count')).group_by('table').join(Table_db).join(Module)
    count_action_uses = History.query.with_entities(History.action, func.count(History.action).label('count')).group_by('action')
    count_users_activity = History.query.with_entities(History.user_id, User.name, User.surname, func.count(History.user_id).label('count')).group_by('user_id').join(User)

    list_for_return = []
    list_for_return1 = []
    list_for_return2 = []

    for use in count_table_uses:
        list_for_return.append({"name":use[1]+' ('+use[2]+')', "y":use[3]})

    for use1 in count_action_uses:
        list_for_return1.append({"name":use1[0], "y":use1[1]})

    for use2 in count_users_activity:
        list_for_return2.append({"name":use2[1]+' '+use2[2], "y":use2[3]})

    response=json.dumps(list_for_return, ensure_ascii=False)
    response2=json.dumps(list_for_return1, ensure_ascii=False)
    response3=json.dumps(list_for_return2, ensure_ascii=False)

    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_count, per_page = 100, css_framework='bootstrap3')

    return render_template("admin/list_history.html", actions_all = actions_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, response = response, response2 = response2, response3=response3)

#Страница с разрешениями всех пользователей
@administration.route('/permissions', methods=['GET', 'POST'])
@login_required
def admin_permissions():
    current_user = get_current_user()
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")

    enter = get_permissions(current_user.role.id, current_user.id, "permissions", "enter")
    insert = get_permissions(current_user.role.id, current_user.id, "permissions", "insert")
    delete = get_permissions(current_user.role.id, current_user.id, "permissions", "delete")
    update = get_permissions(current_user.role.id, current_user.id, "permissions", "update")
    print (update)

    if not enter:
        return forbidden(403)

    permissions_list_roles = Permission.query.filter(Permission.role_id != None).order_by(Permission.role_id.asc(),Permission.table_id.asc())
    permissions_list_users = Permission.query.filter(Permission.user_id != None).order_by(Permission.role_id.asc(),Permission.table_id.asc())

    form_delete = DelPermissionForm()
    form_permission_add = AddPermissionForm()

    if form_delete.validate_on_submit()  and delete:
        permission_id = form_delete.del_id.data
        Permission.query.filter(Permission.id == permission_id).delete()
        make_history("permissions", "удаление", current_user.id)
        db.session.commit()
        flash(u"Разрешение удалено", 'success')
        return redirect(url_for('admin.admin_permissions'))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin_permissions'))

    if form_permission_add.validate_on_submit() and insert:
        if request.method  == 'POST':

            if Permission.query.filter((Permission.user_id == form_permission_add.user_id.data.id)&(Permission.table_id == form_permission_add.table_id.data.id)).first():
                flash(u"Разрешение для данной таблицы и пользователя уже существует. Пожалуйста, найдите его в списке и отредактируйте", 'error')
                return redirect(url_for('admin.admin_permissions'))
            else:
                form_vals = request.form.to_dict()
                permission = Permission(user_id = form_permission_add.user_id.data.id, table_id = form_permission_add.table_id.data.id, enter = form_vals.get('enter'), insert = form_vals.get('insert'), update = form_vals.get('update'), delete = form_vals.get('delete'))
                db.session.add(permission)
                make_history("permissions", "вставку", current_user.id)
                db.session.commit()

                flash(u"Разрешение добавлено", 'success')
                return redirect(url_for('admin.admin_permissions'))
    elif form_permission_add.validate_on_submit() and not insert:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin_permissions'))

    return render_template("admin/list_permissions.html",  all_counters = all_counters,  current_user=current_user, today=today, permissions_list_roles=permissions_list_roles, permissions_list_users=permissions_list_users, form_delete=form_delete, form_permission_add=form_permission_add)

#Быстрое изменение разрешений
@administration.route('/update_permission', methods = ['POST'])
def get_post_javascript_data_show():

    current_user = get_current_user()
    url = 'permissions'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
        permission = request.form['permission']
        state = request.form['state']
        if state=='true':
            state = True
        else:
            state = False

        update_permission = Permission.query.get(permission.split('-')[0])
        if permission.split('-')[1] == "enter":
            update_permission.enter=state
        elif permission.split('-')[1] == "insert":
            update_permission.insert=state
        elif permission.split('-')[1] == "update":
            update_permission.update=state
        elif permission.split('-')[1] == "delete":
            update_permission.delete=state

        db.session.add(update_permission)
        db.session.commit()

        response = app.response_class(
                response=json.dumps({"Успешно":update_permission.id}),
                status=200,
                mimetype='application/json'
            )
        return response
    else:
        flash(u"Вам запрещено данное действие", 'error')
        response = app.response_class(
                response=json.dumps({"Запрещено данное действие":0}),
                status=403,
                mimetype='application/json'
            )
        return response

#Страница со списком новостей
@administration.route('/news', methods=['GET', 'POST'])
@administration.route('/news/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_news(page = 1, *args):

    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "news", "enter")
    print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    news_all = News.query.order_by(News.id.desc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('news_count'), per_page = PER_PAGE, css_framework='bootstrap3')

    form_delete = DelNewsForm()
    delete = get_permissions(current_user.role.id, current_user.id, "news", "delete")
    print ("delete "+str(delete))

    if form_delete.validate_on_submit() and delete:
        news_id = form_delete.del_id.data
        news = News.query.filter(News.id == news_id).first()
        os.remove(os.path.join(app.config['COVERS_FOLDER'], news.cover))
        db.session.delete(news)
        make_history("news", "удаление", current_user.id)
        db.session.commit()
        flash(u"Новость удалена", 'success')
        return redirect(url_for('admin.admin_news', page = page))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('admin.admin_news', page = page))

    return render_template("admin/list_news.html", news_all = news_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today, form_delete=form_delete)

#Быстрое изменение данных записи
@administration.route('/fast_news_edit', methods = ['POST'])
def fast_news_edit():
    current_user = get_current_user()
    url = 'news'

    update = get_permissions(current_user.role.id, current_user.id, url, "update")
    print ("update "+str(update))

    if update:
        request_post = request.form
        edit_news = News.query.get(request_post['pk'])
        if request.method  == 'POST':
            edit_news.header = request_post['value']
            make_history("news", "редактирование", current_user.id)
            db.session.commit()
            flash(u"Запись изменена", 'success')
        response = app.response_class(
            response=json.dumps({u'Успешно изменено!':edit_news.id}),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        flash(u"Вам запрещено данное действие", 'error')
        return jsonify("Запрещено данное действие")

#Форма добавления нового пользователя
@administration.route('/news/new', methods=['GET', 'POST'])
@login_required
def new_news():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "news", "enter")
    print ("enter "+str(enter))
    insert = get_permissions(current_user.role.id, current_user.id, "news", "insert")
    print ("insert "+str(insert))

    if not enter or not insert:
        return forbidden(403)

    today = time.strftime("%Y-%m-%d")

    form_news_add = AddNewsForm()
    all_counters = get_counters()

    if form_news_add.validate_on_submit():
        if request.method  == 'POST':

            cover = request.files['cover']
            if cover:
                hashname = uuid.uuid4().hex + '.' + cover.filename.rsplit('.', 1)[1]
                cover.save(os.path.join(app.config['COVERS_FOLDER'], hashname))
            else:
                hashname = None

            news = News(
            header = form_news_add.header.data,
            text = form_news_add.text.data,
            user_id = current_user.id,
            cover = hashname )

            db.session.add(news)
            make_history("news", "вставку", current_user.id)
            db.session.commit()

            flash(u"Новость добавлена", 'success')
            return redirect(url_for('admin.admin_news'))
    return render_template("admin/add_news.html", form_news_add = form_news_add, all_counters = all_counters, current_user=current_user, today=today)

#Форма изменения новости
@administration.route('/news/edit', methods=['GET', 'POST'])
@login_required
def edit_news():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "news", "enter")
    print ("enter "+str(enter))
    update = get_permissions(current_user.role.id, current_user.id, "news", "update")
    print ("update "+str(update))

    if not enter or not update:
        return forbidden(403)

    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")

    edit_news = News.query.get(request.args.get('id'))

    form_news_edit = EditNewsForm(header=edit_news.header, text=edit_news.text)

    if form_news_edit.validate_on_submit():
        if request.method  == 'POST':

            cover = request.files['cover']
            if cover:
                cover.save(os.path.join(app.config['COVERS_FOLDER'], edit_news.cover))

            edit_news.header = form_news_edit.header.data
            edit_news.text = form_news_edit.text.data

            make_history("news", "редактирование", current_user.id)
            db.session.commit()

            flash(u"Новость изменена", 'success')
            return redirect(url_for('admin.admin_news'))
    return render_template("admin/edit_news.html", form_news_edit = form_news_edit, all_counters = all_counters, current_user=current_user, today=today)

#Страница со списком обращений
@administration.route('/appeals', methods=['GET', 'POST'])
@administration.route('/appeals/<int:page>', methods=['GET', 'POST'])
@login_required
def admin_appeals(page = 1, *args):

    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "appeals", "enter")
    print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    appeals_all = Appeals.query.order_by(Appeals.id.desc()).paginate(page, PER_PAGE, False)
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    pagination = Pagination(page=page, total = all_counters.get('appeals_count_all'), per_page = PER_PAGE, css_framework='bootstrap3')

    return render_template("admin/list_appeals.html", appeals_all = appeals_all, all_counters = all_counters, pagination = pagination,  current_user=current_user, today=today)

#Форма добавления нового обращения
@administration.route('/new_appeals', methods = ['POST', 'GET'])
def new_appeals():
    current_user = get_current_user()

    url = 'appeals'
    insert = get_permissions(current_user.role.id, current_user.id, url, "insert")
    print ("insert "+str(insert))

    if insert:
        request_data = request.form
        if request.method  == 'POST':
            data = Appeals(text=request_data['value'], author = current_user.id)
            db.session.add(data)
            make_history("appeals", "вставку", current_user.id)
            db.session.commit()
            sse.publish({"message": "Поступило новое обращение!"}, type='new', retry=30000)
        destination = url_for('admin.admin_appeals')
        response = Response(
            response=json.dumps({'url':destination,'plus':'<i class="fa fa-plus fa-control" aria-hidden="true"></i>'}),
            status=200,
            mimetype='application/json'
        )
    else:
        flash(u"Вам запрещено данное действие", 'error')
        response = app.response_class(
            response=json.dumps({"Вам запрещено данное действие!":0}),
            status=403,
            mimetype='application/json'
        )
    return response

#Изменение статуса обращения
@administration.route('/appeals_status_change', methods = ['POST'])
def appeals_status_change():
    operation = request.json.items()[0][0]
    id = request.json.items()[0][1]
    appeal = Appeals.query.filter(Appeals.id==id).first()
    appeal_text = ""

    if operation=="done":
        appeal.status = 3
        appeal.ddate = datetime.datetime.now()
        appeal_text = "Исполнено"
        sse.publish({"message": "Статус вашего обращения №_%s изменился на %s"%(appeal.id, appeal_text), "author":appeal.author}, type='message', retry=30)
    elif operation=="get":
        appeal.status = 2
        appeal_text = "Принято"
        sse.publish({"message": "Статус вашего обращения №_%s изменился на %s"%(appeal.id, appeal_text), "author":appeal.author}, type='message', retry=30)
    elif operation=="reject":
        appeal.status = 4
        appeal_text = "Отклонено"
        sse.publish({"message": "Статус вашего обращения №_%s изменился на '%s'"%(appeal.id, appeal_text), "author":appeal.author, "retry":1}, type='message', retry=30)
    elif operation=="checked":
        appeal.status = 5
    db.session.commit()
    return Response(status=200)

#Ответ на обращение
@administration.route('/answer_appeals', methods = ['POST', 'GET'])
def answer_appeals():
    current_user = get_current_user()
    id = request.form['pk']
    appeal = Appeals.query.filter(Appeals.id==id).first()
    appeal.answer = request.form['value']
    db.session.commit()
    sse.publish({"message": "На ваше обращение №_%s получен ответ"%(appeal.id), "author":appeal.author, "retry":30000}, type='message', retry=30)
    response = app.response_class(
        response=json.dumps({"author":appeal.author},{"cuid":current_user.id}),
        status=200,
        mimetype='application/json'
    )
    return response

#Настройки (Придумать потом какие-нибудь настройки)
#~ @administration.route('/options', methods = ['POST', 'GET'])
#~ def options():
    #~ current_user = get_current_user()
    #~ operation = request.json.items()
    #~ resp = make_response()
    #~ resp.set_cookie(operation[0][0],operation[0][1], expires=datetime.datetime.now()+datetime.timedelta(days=365))
    #~ return resp


@administration.route('/users/print', methods=['GET', 'POST'])
@login_required
def admin_users_print(page = 1, *args):

    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "users", "enter")
    print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    users_all = User.query.order_by(User.id.asc()).all()
    today = time.strftime("%Y-%m-%d")

    return render_template("admin/list_users_print.html", users_all = users_all, current_user=current_user, today=today)

@administration.route('/backups/', methods=['GET', 'POST'])
@login_required
def admin_backups(*args):

    current_user = get_current_user()
    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")

    eng_all = create_engine('mysql+pymysql://root:root@localhost')
    excl_list = ['information_schema', 'mysql', 'performance_schema', 'phpmyadmin', 'sys']

    db_list = (inspect(eng_all).get_schema_names())
    for excl in excl_list:
        if excl in db_list:
            db_list.remove(excl)

    eng_all.dispose()

    print (db_list)

    return render_template("admin/backups.html",  current_user=current_user, today=today, all_counters=all_counters, db_list=db_list)





