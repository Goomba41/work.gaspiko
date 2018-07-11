#! venv/bin/python

from app import app, db

from app.models import User, Module, News
from app.API.views import fresh_news_counter

from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response
# ~ from functools import wraps
# ~ from config import basedir, PER_PAGE, SQLALCHEMY_DATABASE_URI, AVATARS_FOLDER
from flask_paginate import Pagination
# ~ from sqlalchemy import create_engine
# ~ from sqlalchemy.sql.functions import func
import time, calendar, os, hashlib, shutil, uuid, json, datetime, inspect, ast, requests
# ~ from collections import defaultdict



#Главная (и единственная) страница
@app.route('/')
def index(page=1):
    users_all = User.query.all()
    modules_all = Module.query.all()
    
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 4, type=int)
    news_all = requests.get(url_for('API.get_all_news', size = size, page = page, _external=True), verify=False)
    pagination = Pagination(page=page, total = News.query.count(), per_page = size, css_framework='bootstrap3')
    
    if page==1:
        fresh_news = fresh_news_counter(news_all, 3)
    else: fresh_news = None
    
    login_as=User.current()
    if page == 1:
        tmpl_name = 'work/index.html'
    else:
        tmpl_name = 'work/items.html'

    return render_template(tmpl_name, users_all = users_all, modules_all=modules_all, news_all=news_all.json(), page=page, login_as=login_as, fresh_news=fresh_news)

@app.route('/news/<int:id>')
def news(id):
    login_as=User.current()
    news = requests.get(url_for('API.get_one_news',news_id=id, _external=True), verify=False).json()
    news_visited = ""
    resp = make_response(render_template("work/news.html", news=news, login_as=login_as))
    if request.cookies.get('news_visited'):
        if str(news['id']) not in request.cookies.get('news_visited').split(' '):
            news_visited = request.cookies.get('news_visited') + ' ' + str(news['id'])
        else:
            news_visited = request.cookies.get('news_visited')
    else:
        news_visited =  str(news['id'])
    resp.set_cookie('news_visited',news_visited, expires=datetime.datetime.now()+datetime.timedelta(days=365))
    return resp
