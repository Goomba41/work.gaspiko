#! venv/bin/python

from app import app, db

from app.authentication.views import login_required
from app.admin.views import get_counters, get_current_user, get_permissions, forbidden, make_history, get_com

#from app.models import Request, Executor, User, Character, Answer, Kind, Send
#from app.kartoteka.forms import DelExecutorForm, AddRequestForm, DelRequestForm, EditRequestForm

from flask import request, make_response, redirect, url_for, render_template, render_template_string, session, flash, g, jsonify, Response, Blueprint, send_from_directory, Markup
from flask_paginate import Pagination
from functools import wraps
from sqlalchemy.sql.functions import func
from sqlalchemy import desc
from config import basedir, SQLALCHEMY_DATABASE_URI, REQUEST_FILES_FOLDER
import time, os, hashlib, json, datetime, csv

zal = Blueprint('zal', __name__, url_prefix='/zal')

@zal.route('/', methods=['GET', 'POST'])
@zal.route('/readers', methods=['GET', 'POST'])
@zal.route('/<int:page>', methods=['GET', 'POST'])
@zal.route('/readers/<int:page>', methods=['GET', 'POST'])
@login_required
def zal_main(page = 1, *args):
    current_user = get_current_user()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    #request_count = Request.query.count()
    #request_in_work_count = Request.query.filter(Request.answer_id==5).count()

    #args = []
    #if (request.args.get('surname')):
        #args.append(Request.surname.like('%%%s%%' % request.args.get('surname')))
    #if (request.args.get('executor')):
        #~ args.append(User.surname.like('%%%s%%' % request.args.get('executor')))
        #args.append(Request.executor_id==request.args.get('executor'))
    #if (request.args.get('number')):
        #~ args.append(Request.number==request.args.get('number'))
        #args.append(Request.number.like('%%%s%%' % request.args.get('number')))
    #if (request.args.get('kind')):
        #args.append(Kind.name==request.args.get('kind'))
    #if (request.args.get('character')):
        #args.append(Character.name==request.args.get('character'))
    #if (request.args.get('answer')):
        #args.append(Answer.name==request.args.get('answer'))
    #if (request.args.get('date_registration')):
        #args.append(Request.date_registration==request.args.get('date_registration'))
    #if (request.args.get('date_done')):
        #args.append(Request.date_done==request.args.get('date_done'))
    #if (request.args.get('date_send')):
        #args.append(Request.date_send==request.args.get('date_send'))
    #if (request.args.get('send')):
        #args.append(Send.name.like('%%%s%%' %request.args.get('send')))

# Для того, чтобы выводил пустых исполнителей, убрать join исполнителей и пользователей, переписать поиск под id исполнителя
    #request_all = Request.query.filter(*args).order_by(Request.date_registration.desc()).join(Executor).join(User).join(Kind).join(Character).join(Answer)
    #request_all = Request.query.filter(*args).order_by(Request.date_registration.desc()).join(Kind).join(Character).join(Answer).join(Send)
    #~ print request_all

    #pages_total = request_all.count()
    #request_all = request_all.paginate(page, 20, False)
    #pagination = Pagination(page=page, total = pages_total, per_page = 20, css_framework='bootstrap3')
    today = time.strftime("%Y-%m-%d")
#
#
    #form_delete = DelRequestForm()
#
    #delete = get_permissions(current_user.role.id, current_user.id, "requests", "delete")
    #print ("delete "+str(delete))
#
    #if form_delete.validate_on_submit() and delete:
        #request_id = form_delete.del_id.data
        #requests = Request.query.filter(Request.id == request_id).first()
        #db.session.delete(requests)
        #if requests.filename:
            #os.remove(os.path.join(REQUEST_FILES_FOLDER, requests.filename))
        #make_history("requests", "удаление", current_user.id)
        #db.session.commit()
        #flash(u"Запрос удален", 'success')
        #return redirect(url_for('kartoteka.kartoteka_main'))
    #elif form_delete.validate_on_submit() and not delete:
        #flash(u"Вам запрещено данное действие", 'error')
        #return redirect(url_for('kartoteka.kartoteka_main'))

    return render_template('zal/mainscreen.html', all_counters=all_counters, today=today, current_user=current_user)
