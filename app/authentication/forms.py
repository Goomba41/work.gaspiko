# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import Required

class LoginForm(FlaskForm):
    login = TextField(u'Логин', validators = [Required(message = u'Введите логин')])
    password = PasswordField(u'Пароль', validators = [Required(message = u'Введите пароль')])
