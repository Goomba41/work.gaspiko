#! venv/bin/python

from app import app, db

from app.authentication.views import login_required
from app.admin.views import get_counters, get_current_user, get_permissions, forbidden, make_history, get_com

from app.models import Request, Executor, User, Character, Answer, Kind, Send
from app.kartoteka.forms import DelExecutorForm, AddRequestForm, DelRequestForm, EditRequestForm

from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response, Blueprint, send_from_directory
from flask_paginate import Pagination
from functools import wraps
from sqlalchemy.sql.functions import func
from sqlalchemy import desc
from config import basedir, SQLALCHEMY_DATABASE_URI, REQUEST_FILES_FOLDER
import time, os, hashlib, json, datetime

kartoteka = Blueprint('kartoteka', __name__, url_prefix='/kartoteka')

@kartoteka.route('/', methods=['GET', 'POST'])
@kartoteka.route('/request', methods=['GET', 'POST'])
@kartoteka.route('/<int:page>', methods=['GET', 'POST'])
@kartoteka.route('/request/<int:page>', methods=['GET', 'POST'])
@login_required
def kartoteka_main(page = 1, *args):
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print "enter "+str(enter)
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    request_count = Request.query.count()

    args = []
    if (request.args.get('surname')):
        args.append(Request.surname.like('%%%s%%' % request.args.get('surname')))
    if (request.args.get('executor')):
        #~ args.append(User.surname.like('%%%s%%' % request.args.get('executor')))
        args.append(Request.executor_id==request.args.get('executor'))
    if (request.args.get('number')):
        #~ args.append(Request.number==request.args.get('number'))
        args.append(Request.number.like('%%%s%%' % request.args.get('number')))
    if (request.args.get('kind')):
        args.append(Kind.name==request.args.get('kind'))
    if (request.args.get('character')):
        args.append(Character.name==request.args.get('character'))
    if (request.args.get('answer')):
        args.append(Answer.name==request.args.get('answer'))
    if (request.args.get('date_registration')):
        args.append(Request.date_registration==request.args.get('date_registration'))
    if (request.args.get('date_done')):
        args.append(Request.date_done==request.args.get('date_done'))
    if (request.args.get('date_send')):
        args.append(Request.date_send==request.args.get('date_send'))
    if (request.args.get('send')):
        args.append(Send.name.like('%%%s%%' %request.args.get('send')))

# Для того, чтобы выводил пустых исполнителей, убрать join исполнителей и пользователей, переписать поиск под id исполнителя
    #request_all = Request.query.filter(*args).order_by(Request.date_registration.desc()).join(Executor).join(User).join(Kind).join(Character).join(Answer)
    request_all = Request.query.filter(*args).order_by(Request.date_registration.desc()).join(Kind).join(Character).join(Answer).join(Send)
    #~ print request_all

    pages_total = request_all.count()
    request_all = request_all.paginate(page, 20, False)
    pagination = Pagination(page=page, total = pages_total, per_page = 20, css_framework='bootstrap3')
    today = time.strftime("%Y-%m-%d")


    form_delete = DelRequestForm()

    delete = get_permissions(current_user.role.id, current_user.id, "requests", "delete")
    print "delete "+str(delete)

    if form_delete.validate_on_submit() and delete:
        request_id = form_delete.del_id.data
        requests = Request.query.filter(Request.id == request_id).first()
        db.session.delete(requests)
        if requests.filename:
            os.remove(os.path.join(REQUEST_FILES_FOLDER, requests.filename))
        make_history("requests", "удаление", current_user.id)
        db.session.commit()
        flash(u"Запрос удален", 'success')
        return redirect(url_for('kartoteka.kartoteka_main'))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('kartoteka.kartoteka_main'))

    return render_template('kartoteka/mainscreen.html', all_counters=all_counters, today=today, current_user=current_user, request_count=request_count, request_all=request_all, pagination=pagination, form_delete = form_delete, pages_total=pages_total)

@kartoteka.route('/executors', methods=['GET', 'POST'])
@login_required
def kartoteka_executors():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "executors", "enter")
    print "enter "+str(enter)
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    executors_all = Executor.query.filter(User.status ==1).join(User).all()

    form_delete = DelExecutorForm()

    delete = get_permissions(current_user.role.id, current_user.id, "executors", "delete")
    print "delete "+str(delete)

    if form_delete.validate_on_submit() and delete:
        executor_id = form_delete.del_id.data
        executors = Executor.query.filter(Executor.id == executor_id).first()
        db.session.delete(executors)
        make_history("executors", "удаление", current_user.id)
        db.session.commit()
        flash(u"Исполнитель удален", 'success')
        return redirect(url_for('kartoteka.kartoteka_executors'))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('kartoteka.kartoteka_executors'))

    request_count = Request.query.count()

    return render_template('kartoteka/list_executors.html', all_counters=all_counters, today=today, current_user=current_user, executors_all=executors_all, form_delete=form_delete, request_count = request_count)

#Получение данных из таблицы и возвращение json в javascript для составления списка пользователей
@kartoteka.route('/get', methods = ['GET'])
def get_users():
    users = User.query.filter((User.id.notin_( Executor.query.with_entities(Executor.user_id)))&(User.status !=0)).all()
    Users_list ={}
    for user in users:
        Users_list.update({str(user.id):"%s %s, %s"%(user.name, user.surname, user.post.name)})
    return jsonify(Users_list)

@kartoteka.route('/add_executor', methods = ['POST'])
def add_executor():
    current_user = get_current_user()

    insert = get_permissions(current_user.role.id, current_user.id, "executors", "insert")
    print "insert "+str(insert)

    if insert:
        request_data = request.form
        if request.method  == 'POST':
            data = Executor(user_id=request_data['value'])
            db.session.add(data)
            make_history("executors", "вставку", current_user.id)
            db.session.commit()
        destination = url_for('kartoteka.kartoteka_executors')
        response = Response(
            response=json.dumps({'url':destination}),
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

@kartoteka.route('/statistics', methods=['GET', 'POST'])
@login_required
def kartoteka_statistics(page = 1, *args):
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print "enter "+str(enter)
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    request_count = Request.query.count()

    today = time.strftime("%Y-%m-%d")

    count_requests_haracter = Request.query.with_entities(Request.character_id, Character.name,func.count(Request.character_id).label('count')).group_by('character_id').order_by(desc('count')).join(Character)
    count_requests_answer = Request.query.with_entities(Request.answer_id, Answer.name,func.count(Request.answer_id).label('count')).group_by('answer_id').order_by(desc('count')).join(Answer)
    count_requests_kind = Request.query.with_entities(Request.kind_id, Kind.name,func.count(Request.kind_id).label('count')).group_by('kind_id').order_by(desc('count')).join(Kind)
    count_requests_year = Request.query.with_entities(func.year(Request.date_registration),func.count("year_1").label('count')).group_by("1").order_by(desc('count'))
    count_requests_users = Request.query.with_entities(Request.executor_id, User.surname, func.count(Request.executor_id).label('count')).group_by(Request.executor_id).order_by(desc('count')).join(Executor).join(User)
    count_requests_users_others = Request.query.filter(Request.executor_id == None).count()
    #~ count_requests_users_2 = Request.query.with_entities(Request.executor_id, User.surname, Answer.name, func.count(Request.executor_id).label('count')).filter((Request.answer_id==3)).group_by(Request.executor_id, Request.answer_id).order_by(desc("count"),User.surname).join(Executor).join(User).join(Answer)


    data = request.json
    result = ""
    if data:
        if data.get('begin') and data.get('end'):

            begin_d = datetime.datetime.strptime(data.get('begin').rsplit("T", 1)[0], '%Y-%m-%d')
            end_d = datetime.datetime.strptime(data.get('end').rsplit("T", 1)[0], '%Y-%m-%d')

            filter_args = []
            group_args = []
            entities_args = []

            filter_args.append(Request.date_done.between(begin_d, end_d))
            entities_args.append(Request.id)

            if int(data.get('type')) == 1:
                filter_args.append(Request.answer_id == 4)
                group_args.append(Request.id)
            if int(data.get('type')) == 2:
                filter_args.append(Request.kind_id == 1)
                group_args.append(Request.id)
            if int(data.get('type')) == 4:
                filter_args.append(Request.kind_id == 2)
                group_args.append(Request.id)
            if int(data.get('type')) == 5:
                entities_args.append(Request.executor_id)
                entities_args.append(User.surname)
                entities_args.append(func.count(Request.executor_id).label('count'))
                entities_args.remove(Request.id)
                group_args.append(Request.executor_id)
                filter_args.append(Request.executor_id != None)
            if int(data.get('type')) == 6:
                group_args.append(Request.id)
                filter_args.append(Request.number.like('%Ю%'))

            if int(data.get('type')) == 5:
                result = Request.query.with_entities(*entities_args).filter(*filter_args).group_by(*group_args).join(Executor, User)
                tmp_list = []
                for i in result:
                    tmp_list.append({"surname":i[1],"col":i[2],"string":get_com(i[2], [u"запрос", u"запроса", u"запросов"])[1]})
                result = {"employee":tmp_list}
            else:
                result = Request.query.with_entities(*entities_args).filter(*filter_args).group_by(*group_args).count()
                result = get_com(result, [u"запрос", u"запроса", u"запросов"])
                result = {"queries":[{"col":str(result[0]),"string":result[1]}]}

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )

        return response

    return render_template('kartoteka/statistics.html', all_counters=all_counters, today=today, current_user=current_user, request_count=request_count, count_requests_haracter=count_requests_haracter, count_requests_answer=count_requests_answer, count_requests_kind=count_requests_kind, count_requests_year=count_requests_year, count_requests_users=count_requests_users, count_requests_users_others=count_requests_users_others)

@kartoteka.route('/request/new', methods=['GET', 'POST'])
@login_required
def new_request_kartoteka():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print "enter "+str(enter)
    insert = get_permissions(current_user.role.id, current_user.id, "requests", "insert")
    print "insert "+str(insert)

    if not enter or not insert:
        return forbidden(403)

    today = time.strftime("%Y-%m-%d")

    form_request_add = AddRequestForm()
    all_counters = get_counters()
    request_count = Request.query.count()

    if form_request_add.validate_on_submit():
        if request.method  == 'POST':

            request_query = Request(
                number = form_request_add.number.data+" "+request.form.get("liter"),
                name = form_request_add.name.data,
                surname = form_request_add.surname.data,
                patronymic = form_request_add.patronymic.data,
                date_registration = form_request_add.date_registration.data,
                kind_id = form_request_add.kind_id.data.id,
                character_id = form_request_add.character_id.data.id,
                executor_id = form_request_add.executor_id.data.id,
                answer_id = 5
            )

            db.session.add(request_query)
            db.session.commit()
            make_history("requests", "вставку", current_user.id)

            flash(u"Запрос добавлен", 'success')
            return redirect(url_for('kartoteka.kartoteka_main'))
    return render_template("kartoteka/add_request.html", form_request_add = form_request_add, all_counters = all_counters, current_user=current_user, today=today, request_count=request_count)

@kartoteka.route('/request/edit', methods=['GET', 'POST'])
@login_required
def edit_request():
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print "enter "+str(enter)
    update = get_permissions(current_user.role.id, current_user.id, "requests", "update")
    print "update "+str(update)

    if not enter or not update:
        return forbidden(403)

    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    request_count = Request.query.count()

    edit_request = Request.query.get(request.args.get('id'))

    liters_str=str(edit_request.number.encode("utf-8"))
    liters_str = liters_str.rsplit(' ')
    print len(liters_str)
    print liters_str
    juridical = 0

    if len(liters_str)==1:
        num = liters_str[0]
        liter = "–".decode("utf-8")
    elif len(liters_str)==2:
        num = liters_str[0]
        liter = liters_str[1].decode("utf-8")
    elif len(liters_str)==3:
        num = liters_str[0]
        liter = liters_str[1].decode("utf-8")
        juridical = 1

    form_request_edit = EditRequestForm(
    number=num,
    copies=edit_request.copies,
    name=edit_request.name,
    surname=edit_request.surname,
    patronymic=edit_request.patronymic,
    date_registration=edit_request.date_registration,
    date_done=edit_request.date_done,
    date_send=edit_request.date_send,
    kind_id=edit_request.kind_id,
    character_id=edit_request.character_id,
    executor_id=edit_request.executor_id,
    send_id=edit_request.send_id,
    answer_id=edit_request.answer_id,
    filename = edit_request.filename
    )


    if form_request_edit.validate_on_submit():
        if request.method  == 'POST':
            print request.form
            filename = request.files['filename']
            if filename:
                if edit_request.filename is not None:
                    filename.save(os.path.join(REQUEST_FILES_FOLDER, edit_request.filename))
                else:
                    name = today + '_' + str(edit_request.number) + '_' + str(edit_request.id) + '.' + filename.filename.rsplit('.', 1)[1]
                    filename.save(os.path.join(REQUEST_FILES_FOLDER, name))
                    edit_request.filename = name

            num = form_request_edit.number.data + " " + request.form.get('liter')

            edit_request.number=num
            edit_request.copies=int(form_request_edit.copies.data)
            edit_request.name=form_request_edit.name.data
            edit_request.surname=form_request_edit.surname.data
            edit_request.patronymic=form_request_edit.patronymic.data
            edit_request.date_registration=form_request_edit.date_registration.data
            edit_request.date_done=form_request_edit.date_done.data
            edit_request.date_send=form_request_edit.date_send.data
            edit_request.kind_id=form_request_edit.kind_id.data
            edit_request.character_id=form_request_edit.character_id.data
            edit_request.executor_id=form_request_edit.executor_id.data
            edit_request.send_id=form_request_edit.send_id.data
            edit_request.answer_id=form_request_edit.answer_id.data

            make_history("requests", "редактирование", current_user.id)
            db.session.commit()

            flash(u"Запрос изменен", 'success')
            return redirect(url_for('kartoteka.edit_request', id=edit_request.id))
    return render_template("kartoteka/edit_request.html", form_request_edit=form_request_edit, all_counters = all_counters, current_user=current_user, today=today,request_count=request_count, edit_request=edit_request, liter=liter, juridical=juridical)


#~ @kartoteka.route('/search', methods = ['POST','GET'])
#~ def print_post(page = 1, *args):
    #~ jsdata = request.get_json()
    #~ print jsdata.get('surname')
#~
    #~ response = Response(
        #~ response=json.dumps({'OK':"OK"}),
        #~ status=200,
        #~ mimetype='application/json'
    #~ )
    #~ return response

@kartoteka.route('/upload/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(basedir, REQUEST_FILES_FOLDER)
    return send_from_directory(directory=uploads, filename=filename)

@kartoteka.route('/delete/<path:filename>', methods=['GET', 'POST'])
def delete_file(filename):
    requests = Request.query.get(request.form['id_request'])
    os.remove(os.path.join(REQUEST_FILES_FOLDER, requests.filename))
    requests.filename = None
    db.session.commit()
    response = Response(
        response=json.dumps({'OK':'OK'}),
        status=200,
        mimetype='application/json'
    )
    return response

@kartoteka.route('/request/search', methods=['GET', 'POST'])
@login_required
def search_request():
    executors = Executor.query.join(User).all()
    kinds = Kind.query.all()
    characters = Character.query.all()
    answers = Answer.query.all()
    sends = Send.query.all()

    today = time.strftime("%Y-%m-%d")
    current_user = get_current_user()
    all_counters = get_counters()
    request_count = Request.query.count()

    return render_template('kartoteka/search.html', all_counters=all_counters, today=today, current_user=current_user, request_count=request_count, executors=executors, kinds=kinds, characters=characters, answers=answers, sends=sends)
