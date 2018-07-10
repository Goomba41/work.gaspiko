#! venv/bin/python

import json, math, requests, os
from app import app, db

from app.models import News, NewsSchema
from flask import request, make_response, jsonify, Response, Blueprint, url_for
from datetime import datetime

API = Blueprint('API', __name__, url_prefix='/API/v1.0')

#----------------------------------------------------------------------------------
# ФУНКЦИИ
#----------------------------------------------------------------------------------

#Пагинация списка, полученного из API
def paginate_list(page, size, lst):
    
    total = len(lst)
    page = int(page)
    size = int(size)

    pages = math.ceil(total/size)

    
    if page == 1:
        lft = page * size
        for x in range(total):
            if lft != 0:
                lft = lft -1
            else:
                lst.pop(size)
    elif page == pages:
        lft = (page-1) * size
        for x in range(total):
            if lft != 0:
                lft = lft -1
                lst.pop(0)
    else:
        lft = (page-1) * size
        rgt = total - size - lft
        for x in range(total):
            if lft != 0:
                lft = lft -1
                lst.pop(0)
            elif lft == 0:
                if rgt != 0:
                    rgt = rgt - 1
                    lst.pop(size)

    return lst


#Функция обработки склонений
def get_declension(x, y):
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
    
#Фильтр для дат для шаблонизатора 
def format_datetime(value, format='medium'):
    date=value.split("T")[0] 
    time=value.split("+")[0].split("T")[1]

    datetime_object = datetime.strptime(date+" "+time, "%Y-%m-%d %H:%M:%S")

    if format == 'full':
        format=datetime.strftime(datetime_object, "%Y-%m-%d в %H:%M:%S")
    elif format == 'medium':
        format=datetime.strftime(datetime_object, "%Y-%m-%d")
    elif format == 'since':
        now = datetime.now()
        diff = now - datetime_object

        periods = (
            (diff.seconds, [u"секунда", u"секунды", u"секунд"]),
            (diff.seconds / 60, [u"минута", u"минуты", u"минут"]),
            (diff.seconds / 3600, [u"час", u"часа", u"часов"]),
            (diff.days, [u"день", u"дня", u"дней"]),
            (diff.days / 7, [u"неделя", u"недели", u"недель"]),
            (diff.days / 30, [u"месяц", u"месяца", u"месяцев"]),
            (diff.days / 365, [u"год", u"года", u"лет"]),
        )
        
        for period, declension in periods:
            period = int(round(period,0))
            if period!=0:
                period = get_declension(period, declension)
                format = "%d %s назад" % (period[0], period[1])

    return format

app.jinja_env.filters['datetime'] = format_datetime
    
#----------------------------------------------------------------------------------
# НОВОСТИ НА ВНЕШНЕЙ
#----------------------------------------------------------------------------------

#Список всех новостей
@API.route('/news', methods=['GET'])
def get_all_news():
    
    news = News.query.all()
    news_schema = NewsSchema()
    
    news_lst = []
    for n in news:
        news_lst.append(news_schema.dump(n).data)
    news_lst.reverse()
        
    if (request.args.get('page') and request.args.get('size')):
        response = jsonify(paginate_list(request.args.get('page'), request.args.get('size'), news_lst))
    else:
        response = jsonify(news_lst)
    
    return response
    
#Одна новость
@API.route('/news/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    
    news = News.query.filter(News.id==news_id).first()
    news_schema = NewsSchema()

    response = jsonify(news_schema.dump(news).data)
    
    return response

#Удаление новости
@API.route('/news/<int:news_id>', methods=['DELETE'])
def delete_one_news(news_id):
    
    news = News.query.filter(News.id == news_id).first()
    # ~ for image in news.images:
        # ~ os.remove(os.path.join(app.config['NEWS_IMAGES_FOLDER_ROOT'], image['filename']))
    # ~ db.session.delete(news)
    # ~ db.session.commit()

    response = jsonify(news_id)
    
    return response
