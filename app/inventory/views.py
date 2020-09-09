#! env/bin/python3.8

from app import app, db

from app.authentication.views import login_required
from app.admin.views import get_counters, get_permissions, forbidden

from app.models import User, Item, Executor

from flask import make_response, url_for, render_template, jsonify, Response, Blueprint, request
from flask_paginate import Pagination
import time, os, hashlib, json, datetime, requests

inventory = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory.route('/', methods=['GET', 'POST'])
@inventory.route('/items', methods=['GET', 'POST'])
@login_required
def inventory_main(page = 1, *args):
    current_user = User.current()
    
    can = User.can("enter","items")
    if not can:
        return forbidden(403)

    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")

    args = request.args.to_dict()
    args['page'] = request.args.get('page', 1, type=int)
    args['size'] = request.args.get('size', 4, type=int)

    # items_all = requests.get(url_for('API.get_all_inventory_items', size = size, page = page, _external=True), verify=False)
    # print(url_for('API.get_all_inventory_items', **args, _external=True))
    items_all = requests.get(url_for('API.get_all_inventory_items', **args, _external=True), verify=False).json()
    # print(len(items_all[0]))
    pagination = Pagination(page=args['page'], total = items_all[1], per_page = args['size'], css_framework='bootstrap4')
    # pagination = Pagination(page=args['page'], total = Item.query.count(), per_page = args['size'], css_framework='bootstrap4')

    return render_template('inventory/mainscreen.html', all_counters=all_counters, today=today, items=items_all[0], pagination=pagination)

#Форма добавления нового объекта
@inventory.route('/items/new', methods=['GET', 'POST'])
@login_required
def new_items():
    
    c_user = User.current()
    
    can = User.can("enter","items") and User.can("insert","items")
    if not can:
        return forbidden(403)

    all_counters = get_counters()
    
    name_list = User.get_pylist()

    return render_template("inventory/add_item.html", all_counters = all_counters, name_list=name_list)
    
#Форма редактирования объекта
@inventory.route('/items/edit', methods=['GET', 'POST'])
@login_required
def edit_items():
    
    c_user = User.current()
    
    can = User.can("enter","items") and User.can("update","items")
    if not can:
        return forbidden(403)

    all_counters = get_counters()
    
    edit_items = Item.query.get(request.args.get('id'))
    
    name_list = User.get_pylist()

    return render_template("inventory/edit_item.html", all_counters = all_counters, name_list=name_list, edit_items=edit_items)

#Форма поиска объекта
@inventory.route('/items/search', methods=['GET', 'POST'])
@login_required
def search_items():
    
    c_user = User.current()
    
    can = User.can("enter","items")
    if not can:
        return forbidden(403)

    all_counters = get_counters()
    
    name_list = User.get_pylist()

    return render_template("inventory/search.html", all_counters = all_counters, name_list=name_list)
    



    

