#! venv/bin/python

from app import app, db

from app.authentication.views import login_required
from app.admin.views import get_counters, get_current_user, get_permissions, forbidden, make_history

from app.models import Request, Executor, User, Character, Answer, Kind
from app.kartoteka.forms import DelExecutorForm

from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response, Blueprint
from flask_paginate import Pagination
from functools import wraps
from sqlalchemy.sql.functions import func
from sqlalchemy import desc
from config import basedir, SQLALCHEMY_DATABASE_URI
import time, os, hashlib, json, datetime

kartoteka = Blueprint('kartoteka', __name__, url_prefix='/kartoteka')

@kartoteka.route('/', methods=['GET', 'POST'])
@kartoteka.route('/<int:page>', methods=['GET', 'POST'])
@login_required
def kartoteka_main(page = 1, *args):
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print "enter "+str(enter)
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    request_count = Request.query.count()
    request_all = Request.query.order_by(Request.date_registration.desc()).paginate(page, 20, False)
    pagination = Pagination(page=page, total = request_count, per_page = 20, css_framework='bootstrap3')
    today = time.strftime("%Y-%m-%d")

    return render_template('kartoteka/mainscreen.html', all_counters=all_counters, today=today, current_user=current_user, request_count=request_count, request_all=request_all, pagination=pagination)

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
        make_history("news", "удаление", current_user.id)
        db.session.commit()
        flash(u"Исполнитель удален", 'success')
        return redirect(url_for('kartoteka.kartoteka_executors'))
    elif form_delete.validate_on_submit() and not delete:
        flash(u"Вам запрещено данное действие", 'error')
        return redirect(url_for('kartoteka.kartoteka_executors'))

    return render_template('kartoteka/list_executors.html', all_counters=all_counters, today=today, current_user=current_user, executors_all=executors_all, form_delete=form_delete)

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


    return render_template('kartoteka/statistics.html', all_counters=all_counters, today=today, current_user=current_user, request_count=request_count, count_requests_haracter=count_requests_haracter, count_requests_answer=count_requests_answer, count_requests_kind=count_requests_kind, count_requests_year=count_requests_year)
