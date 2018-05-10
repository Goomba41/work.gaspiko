#! venv/bin/python

import json, math, requests
from app import app, db

from app.models import News, NewsSchema
from flask import request, make_response, jsonify, Response, Blueprint, url_for

API = Blueprint('API', __name__, url_prefix='/API/v1.0')

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


#Список всех новостей
@API.route('/news', methods=['GET'])
def get_all_news():
    
    news = News.query.all()
    news_schema = NewsSchema()
    
    news_lst = []
    for n in news:
        news_lst.append(news_schema.dump(n).data)
        
    if (request.args.get('page') and request.args.get('size')):
        print(request.args.get('page'), request.args.get('size'))
        response = jsonify(paginate_list(request.args.get('page'), request.args.get('size'), news_lst))
    else:
        response = jsonify(news_lst)
    
    return response
