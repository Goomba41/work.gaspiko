﻿#! venv/bin/python

import json, math, requests, os
from app import app, db

from app.models import News, NewsSchema, User, Item, ItemSchema
from flask import request, make_response, jsonify, Response, Blueprint, url_for, json
from dateutil.relativedelta import relativedelta
import datetime, calendar
from sqlalchemy.orm.attributes import flag_modified
import hashlib, uuid


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
    
#Функция форматирования строчной даты в объект даты
def datestring_to_object(value):
    date=value.split("T")[0] 
    time=value.split("+")[0].split("T")[1]

    datetime_object = datetime.datetime.strptime(date+" "+time, "%Y-%m-%d %H:%M:%S")
    return (datetime_object)
    
#Фильтр для дат для шаблонизатора 
def format_datetime(value, format='medium'):

    datetime_object = datestring_to_object(value)

    if format == 'full':
        format=datetime.datetime.strftime(datetime_object, "%Y-%m-%d в %H:%M:%S")
    elif format == 'medium':
        format=datetime.datetime.strftime(datetime_object, "%Y-%m-%d")
    elif format == 'since':
        now = datetime.datetime.now()
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

#Фильтр для определения истечения проверки для шаблонизатора 
def expiration_of_date(value, period='month', number=3):

    datetime_of_check = datestring_to_object(value)
    
    now = datetime.datetime.now()
    without_check = now - datetime_of_check # сколько дней не проверялось
    
    if period == 'day':
        should_be_checked = (datetime_of_check + relativedelta(days=+number))-datetime_of_check
    elif period == 'week':
        should_be_checked = (datetime_of_check + relativedelta(weeks=+number))-datetime_of_check
    elif period == 'month':
        should_be_checked = (datetime_of_check + relativedelta(months=+number))-datetime_of_check
    elif period == 'year':
        should_be_checked = (datetime_of_check + relativedelta(years=+number))-datetime_of_check

    if (without_check <= should_be_checked*0.33):
        color = "green"
    elif (without_check > should_be_checked*0.33 and without_check <= should_be_checked*0.66):
        color = "yellow"
    elif (without_check > should_be_checked*0.66 and without_check <= should_be_checked*0.99):
        color = "orange"
    elif (without_check > should_be_checked*0.99):
        color = "red"

    return (color)

app.jinja_env.filters['expiration'] = expiration_of_date

#Функция для шаблонизатора для подсчета количества объектов с истекшим сроком проверки
@app.context_processor
def utility_processor():
    def count_of_expired(period='month', number=3):
        
        items_all = requests.get(url_for('API.get_all_inventory_items', _external=True), verify=False)
        items_all = items_all.json()
        
        now = datetime.datetime.now()
        expired_items = []
                
        for item in items_all:
            if item["chdate"] is not None:
                if (expiration_of_date(item["chdate"], period = period, number = number) == "red"):
                    expired_items.append(item)
            else:
                expired_items.append(item)
                
        procent = round((len(expired_items)/len(items_all))*100, 1)
                
        if (procent <= 66):
            color = "info"
        elif (procent > 66 and procent <= 90):
            color = "warning"
        elif (procent > 90):
            color = "danger"
                
        return (len(expired_items), procent, color)
    return dict(count_of_expired=count_of_expired)

#Проверка новости на свежесть
def fresh_news(value,days):

    datetime_object = datestring_to_object(value)
    now = datetime.now()
    diff = now - datetime_object
    
    if diff.days<=int(days):
        return True
    else:
        return False
        
app.jinja_env.filters['fresh'] = fresh_news

#Подсчет свежих новостей
def fresh_news_counter(news_list,days):
    count = 0
    for i in news_list.json():
        if fresh_news(i['cdate'],days):
            count += 1
        else: break

    return (count)

#----------------------------------------------------------------------------------
# API НОВОСТЕЙ
#----------------------------------------------------------------------------------

#Список всех новостей
@API.route('/news', methods=['GET'])
def get_all_news():
    
    news = News.query.all()
    news_schema = NewsSchema()
    
    tmp = []
    for n in news:
        tmp.append(news_schema.dump(n).data)
    news_lst = sorted(tmp, key=lambda k: k['cdate'],reverse=True) 
        
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
    
    can = User.can("delete","news")
    
    if can:
        news = News.query.filter(News.id == news_id).first()
        for image in news.images:
            os.remove(os.path.join(app.config['NEWS_IMAGES_FOLDER_ROOT'], image['filename']))
        db.session.delete(news)
        db.session.commit()

        response = jsonify(news_id)
    else:
        response = Response(
            response=json.dumps({'type':'fail', 'text':'Пользователю запрещено удаление!'}),
            status=403,
            mimetype='application/json'
        )
    
    return response
    
#Добавление новости
@API.route('/news', methods=['POST'])
def post_news():
    
    c_user = User.current()
    can = User.can("insert","news")
    
    if can:
        try:
            form_data = json.loads(request.form['data'])

            images_list = []
            if request.files:
                time_hash = uuid.uuid1().hex
                cover_by_default = False
                for image in request.files.getlist("images"):
                    hashname = time_hash+'.'+uuid.uuid4().hex + '.' + image.filename.rsplit('.', 1)[1]
                    image.save(os.path.join(app.config['NEWS_IMAGES_FOLDER_ROOT'], hashname))
                    if not cover_by_default :
                        images_list.append({'filename':hashname, 'as_cover':1, 'in_gallery':0, 'position':0})
                        cover_by_default = True
                    else:
                        images_list.append({'filename':hashname, 'as_cover':0, 'in_gallery':0, 'position':0})

            news = News(
            header = form_data['header'],
            text = form_data['text'],
            user_id = c_user.id,
            images = images_list )

            db.session.add(news)
            db.session.commit()
            
            n_list=url_for('admin.admin_news')
            n_edit=url_for('admin.edit_news', id=news.id)

            response = Response(
                response=json.dumps({'type':'success', 'text':'Добавлено!', 'list':n_list, 'edit':n_edit}),
                status=200,
                mimetype='application/json'
            )
        except:
            response = Response(
            response=json.dumps({'type':'fail', 'text':'Серверная ошибка!'}),
            status=500,
            mimetype='application/json'
            )
            return response
    else:
        response = Response(
            response=json.dumps({'type':'fail', 'text':'Пользователю запрещено добавление!'}),
            status=403,
            mimetype='application/json'
        )
    
    return response
    
#Редактирование новости новости
@API.route('/news/<int:news_id>', methods=['PUT'])
def update_news(news_id):
    
    c_user = User.current()
    can = User.can("update","news")
    
    if can:
        try:
            form_data = json.loads(request.form['data'])
            edit_news = News.query.get(news_id)
            
            if request.files:
                if (request.files.getlist("images")[0].filename!=''):
                    if edit_news.images:
                        images_list = edit_news.images[:] #Клонирование существующего списка
                    else:
                        images_list = []
                    time_hash = uuid.uuid1().hex
                    for image in request.files.getlist("images"):
                        hashname = time_hash+'.'+uuid.uuid4().hex + '.' + image.filename.rsplit('.', 1)[1]
                        image.save(os.path.join(app.config['NEWS_IMAGES_FOLDER_ROOT'], hashname))
                        images_list.append({'filename':hashname, 'as_cover':0, 'in_gallery':0, 'position':0})
                        edit_news.images = images_list
                        
            
            edit_news.header = form_data['header']
            edit_news.text = form_data['text']
            
            db.session.commit()
            
            
            n_list=url_for('admin.admin_news')
            n_new=url_for('admin.new_news')
            

            response = Response(
                response=json.dumps({'type':'success', 'text':'Изменения сохранены!', 'list':n_list, 'new':n_new}),
                status=200,
                mimetype='application/json'
            )
        except:
            response = Response(
            response=json.dumps({'type':'fail', 'text':'Серверная ошибка!'}),
            status=500,
            mimetype='application/json'
            )
            return response
    else:
        response = Response(
            response=json.dumps({'type':'fail', 'text':'Пользователю запрещено изменение!'}),
            status=403,
            mimetype='application/json'
        )
    
    return response
    
#Редактирование изображений новости новости
@API.route('/news/<int:news_id>/images', methods=['PUT'])
def update_news_images(news_id):
    
    c_user = User.current()
    can = User.can("update","news")
    
    if can:
        try:
            edit_news = News.query.get(news_id)

            if (request.form['action'] == 'delete'):
                
                images = edit_news.images[:]
                images[:] = [d for d in images if d.get('filename') != request.form['filename']]

                os.remove(os.path.join(app.config['NEWS_IMAGES_FOLDER_ROOT'], request.form['filename']))

                edit_news.images = images
                db.session.commit()
                
                response = Response(
                    response=json.dumps({'type':'success', 'action':'delete', 'text':'Изображение удалено!'}),
                    status=200,
                    mimetype='application/json'
                )
                
            elif (request.form['action'] == 'as_cover'):

                for image in edit_news.images:
                    if image['filename'] == request.form['filename']:
                        image['as_cover'] = 1
                        image['in_gallery'] = 0
                    elif image['as_cover'] == 1:
                        prev_id = image['filename']
                        image['as_cover'] = 0

                flag_modified(edit_news, "images")
                db.session.commit()
                
                response = Response(
                    response=json.dumps({'type':'success', 'action':'as_cover', 'text':'Отмечено как обложка!', 'prev_id':prev_id}),
                    status=200,
                    mimetype='application/json'
                )
                
            elif (request.form['action'] == 'in_gallery'):
                
                for image in edit_news.images:
                    if image['filename'] == request.form['filename']:
                        if image['in_gallery'] == 1:
                            image['as_cover'] = 0
                            image['in_gallery'] = 0
                            text = 'Убрано из галереи!'
                            make = 'remove'
                        else:
                            image['as_cover'] = 0
                            image['in_gallery'] = 1
                            text = 'Добавлено в галерею!'
                            make = 'add'
                        if 'gallery_title' in image:
                            title=image['gallery_title']
                        else:
                            title=''

                flag_modified(edit_news, "images")
                db.session.commit()
                                
                response = Response(
                    response=json.dumps({'type':'success', 'action':'in_gallery', 'text':text, 'make':make, 'gallery_title':title}),
                    status=200,
                    mimetype='application/json'
                )
                
            elif (request.form['action'] == 'gallery_title'):
                for image in edit_news.images:
                    if image['filename'] == request.form['filename']:
                        image.update({"gallery_title":request.form['gallery_title']})

                flag_modified(edit_news, "images")
                db.session.commit()
                                
                response = Response(
                    response=json.dumps({'type':'success', 'action':'gallery_title', 'text':'Заголовок сохранен!'}),
                    status=200,
                    mimetype='application/json'
                )
                
        except:
            response = Response(
            response=json.dumps({'type':'fail', 'text':'Серверная ошибка!'}),
            status=500,
            mimetype='application/json'
            )
    else:
        response = Response(
            response=json.dumps({'type':'fail', 'text':'Пользователю запрещено изменение!'}),
            status=403,
            mimetype='application/json'
        )
    
    return response

#----------------------------------------------------------------------------------
# API ПОЛЬЗОВАТЕЛЕЙ СИСТЕМЫ
#----------------------------------------------------------------------------------


#----------------------------------------------------------------------------------
# API ИНВЕНТАРИЗАЦИИ
#----------------------------------------------------------------------------------

#Одна штучка
@API.route('/inventar/<int:id>', methods=['GET'])
@API.route('/inventar/id/<int:id>', methods=['GET'])
def get_one_inventory_item(id):
    
    item = Item.query.filter(Item.id==id).first()
    item_schema = ItemSchema()

    response = jsonify(item_schema.dump(item).data)
    
    return response
    
#Все штучки
@API.route('/inventar', methods=['GET'])
def get_all_inventory_items():
    
    items = Item.query.all()
    item_schema = ItemSchema()
    
    tmp = []
    for item in items:
        tmp.append(item_schema.dump(item).data)
    items_lst = sorted(tmp, key=lambda k: k['id'],reverse=True) 
            
    if (request.args.get('page') and request.args.get('size')):
        response = jsonify(paginate_list(request.args.get('page'), request.args.get('size'), items_lst))
    else:
        response = jsonify(items_lst)
    
    return response

#Поиск штучки по инвентарнику
@API.route('/inventar/in/<string:number>', methods=['GET'])
def get_one_inventory_item_by_in(number):
    
    item = Item.query.filter(Item.number==number).first()
    item_schema = ItemSchema()

    response = jsonify(item_schema.dump(item).data)
    
    return response

#Удаление объекта
@API.route('/inventar/<int:id>', methods=['DELETE'])
@API.route('/inventar/id/<int:id>', methods=['DELETE'])
def delete_one_item(id):
    
    can = User.can("delete","items")
    
    if can:
        item = Item.query.filter(Item.id == id).first()
        db.session.delete(item)
        db.session.commit()

        response = jsonify(id)
    else:
        response = Response(
            response=json.dumps({'type':'fail', 'text':'Пользователю запрещено удаление!'}),
            status=403,
            mimetype='application/json'
        )
    
    return response

    
#Добавление объекта
@API.route('/inventar', methods=['POST'])
def post_item():
    
    c_user = User.current()
    can = User.can("insert","items")
    
    if can:       
        try:
            form_data = json.loads(request.form['data'])

            keys = ['floor', 'room', 'description']
            placing = {x:form_data[x] for x in keys}

            for k,v in form_data.items(): 
                if form_data[k] == '':
                    form_data[k] = None

            item = Item(
            name = form_data['name'],
            number = form_data['number'],
            responsible = form_data['responsible'],
            placing = placing,
            employee = form_data['employee'],
            serial = form_data['serial'],
            status = 1)

            db.session.add(item)
            db.session.commit()
            
            n_list=url_for('inventory.inventory_main')
            n_edit=url_for('inventory.edit_items', id=item.id)

            response = Response(
                response=json.dumps({'type':'success', 'text':'Добавлено!', 'list':n_list, 'edit':n_edit}),
                status=200,
                mimetype='application/json'
            )
        except:
            response = Response(
            response=json.dumps({'type':'fail', 'text':'Серверная ошибка!'}),
            status=500,
            mimetype='application/json'
            )
            return response
    else:
        response = Response(
            response=json.dumps({'type':'fail', 'text':'Пользователю запрещено добавление!'}),
            status=403,
            mimetype='application/json'
        )
    
    return response

#Редактирование объекта
@API.route('/inventar/<int:id>', methods=['PUT'])
def update_item(id):
    
    c_user = User.current()
    can = User.can("update","items")
    
    if can:
        try:
            form_data = json.loads(request.form['data'])
            for k,v in form_data.items(): 
                if form_data[k] == '':
                    form_data[k] = None
            edit_item = Item.query.get(id)
            
            if ((form_data['floor'] != edit_item.placing['floor']) or (form_data['room'] != edit_item.placing['room'])):
                print("Местоположение изменилось")
                if edit_item.movements is None:
                    print("Не было перемещений")
                else:
                    # edit_item.movements.append({"to": "4-17", "date": "2018-11-06 15:45:14", "from": "2-15", "description": ""})
                
# [{"to": "4-17", "date": "2018-11-06 15:45:14", "from": "2-15", "description": "Убран сервер, поставлен пользователю"}]
            
            edit_item.name = form_data['name']
            edit_item.number = form_data['number']
            edit_item.responsible = form_data['responsible']
            edit_item.employee = form_data['employee']
            edit_item.serial = form_data['serial']
                        
            db.session.commit()
            
            n_list=url_for('inventory.inventory_main')
            n_new=url_for('inventory.new_items')           

            response = Response(
                response=json.dumps({'type':'success', 'text':'Изменения сохранены!', 'list':n_list, 'new':n_new}),
                status=200,
                mimetype='application/json'
            )
        except:
            response = Response(
            response=json.dumps({'type':'fail', 'text':'Серверная ошибка!'}),
            status=500,
            mimetype='application/json'
            )
            return response
    else:
        response = Response(
            response=json.dumps({'type':'fail', 'text':'Пользователю запрещено изменение!'}),
            status=403,
            mimetype='application/json'
        )
    
    return response



#Отметка объекта как проверенного
@API.route('/inventar/check/<int:item_id>', methods=['PUT'])
def checked_one_inventory_item(item_id):
    
    item = Item.query.get(item_id)

    item.status = 2
    
    db.session.commit()

    response = jsonify("Отмечено!")
    
    return response
