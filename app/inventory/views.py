#! venv/bin/python

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

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")
    
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 2, type=int)
    items_all = requests.get(url_for('API.get_all_inventory_items', size = size, page = page, _external=True), verify=False)
    pagination = Pagination(page=page, total = Item.query.count(), per_page = size, css_framework='bootstrap4')

    return render_template('inventory/mainscreen.html', all_counters=all_counters, today=today, items=items_all.json(), pagination=pagination)


    



    

