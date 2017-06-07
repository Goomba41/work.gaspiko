#! venv/bin/python

from app import app, db

from app.models import User, Module, News

from app.admin.views import get_counters


from flask import request, make_response, redirect, url_for, render_template, session, flash, g, jsonify, Response
from functools import wraps
from config import basedir, PER_PAGE, SQLALCHEMY_DATABASE_URI, AVATARS_FOLDER
from flask_paginate import Pagination
from sqlalchemy import create_engine
from sqlalchemy.sql.functions import func
import time, calendar, os, hashlib, shutil, uuid, json, datetime, inspect, ast, redis
from flask_sse import sse
from collections import defaultdict


#Главная (и единственная) страница
@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    all_counters = get_counters()
    users_all = User.query.all()
    modules_all = Module.query.all()
    news_all = News.query.order_by(News.id.desc()).paginate(page, 4, False).items
    tmpl_name = ''
    if page == 1:
        tmpl_name = 'work/index.html'
    else:
        tmpl_name = 'work/items.html'
    #~ print tmpl_name, news_all
    if request.cookies.get('news_visited'):
        news_visited = request.cookies.get('news_visited').split(' ')
    else:
        news_visited = []
    return render_template(tmpl_name, users_all = users_all, modules_all=modules_all, news_all=news_all, page=page, news_visited=news_visited)

@app.route('/news/<int:id>')
def news(id):
    news = News.query.filter(News.id==id).first()
    news_visited = ""
    resp = make_response(render_template("work/news.html", news=news))
    if request.cookies.get('news_visited'):
        if str(news.id) not in request.cookies.get('news_visited').split(' '):
            news_visited = request.cookies.get('news_visited') + ' ' + str(news.id)
        else:
            news_visited = request.cookies.get('news_visited')
    else:
        news_visited =  str(news.id)
    resp.set_cookie('news_visited',news_visited, expires=datetime.datetime.now()+datetime.timedelta(days=365))
    return resp
