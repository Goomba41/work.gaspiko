#! venv/bin/python

from app import app, db

from app.authentication.views import login_required
from app.admin.views import get_counters, get_permissions, forbidden

from app.models import User

from flask import make_response, url_for, render_template, jsonify, Response, Blueprint
from flask_paginate import Pagination
import time, os, hashlib, json, datetime

inventory = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory.route('/', methods=['GET', 'POST'])
@inventory.route('/items', methods=['GET', 'POST'])
@inventory.route('/<int:page>', methods=['GET', 'POST'])
@inventory.route('/items/<int:page>', methods=['GET', 'POST'])
@login_required
def inventory_main(page = 1, *args):
    current_user = User.current()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    today = time.strftime("%Y-%m-%d")


    return render_template('inventory/mainscreen.html', all_counters=all_counters, today=today, current_user=current_user)
