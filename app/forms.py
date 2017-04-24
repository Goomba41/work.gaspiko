# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import TextField, PasswordField
from wtforms.validators import Required, regexp, Length

class LoginForm(FlaskForm):
    login = TextField(u'Логин', validators = [Required(message = u'Введите логин')])
    password = PasswordField(u'Пароль', validators = [Required(message = u'Введите пароль')])

class DelUserForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])
