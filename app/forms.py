# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import TextField, PasswordField, DateField, SelectField
from wtforms.validators import Required, regexp, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from models import Department, Role, Post
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class LoginForm(FlaskForm):
    login = TextField(u'Логин', validators = [Required(message = u'Введите логин')])
    password = PasswordField(u'Пароль', validators = [Required(message = u'Введите пароль')])

class AddUserForm(FlaskForm):

    login = TextField(u'Логин', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Логин должен быть в диапазоне от 1 до 15 символов')])
    password = PasswordField(u'Пароль', validators = [Required(message = u'Введите пароль'), Length(min=1, message = u'Пароль должен быть более 8 символов')])
    photo = FileField(u'Выберите фото профиля')
    surname = TextField(u'Фамилия', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Фамилия должна быть в диапазоне от 1 до 15 символов')])
    name= TextField(u'Имя', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Имя должно быть в диапазоне от 1 до 15 символов')])
    patronymic = TextField(u'Отчетство', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Отчество должно быть в диапазоне от 1 до 15 символов')])
    email = TextField(u'Почта', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=50, message = u'Отчество должно быть в диапазоне от 1 до 50 символов')])
    phone = TextField(u'Телефон', validators = [Required(message = u'Поле не может быть пустым')])
    birth_date = DateField(u'Дата рождения', id=1, validators = [Required(message = u'Поле не может быть пустым')])
    work_date = DateField(u'В должности с', id=2, validators = [Required(message = u'Поле не может быть пустым')])

    department_id = QuerySelectField(u'Отдел', get_label=lambda x: x.name, query_factory=lambda: Department.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])
    post_id = QuerySelectField(u'Должность', get_label=lambda x: x.name,  query_factory=lambda: Post.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])
    role_id = QuerySelectField(u'Роль', get_label=lambda x: x.name,  query_factory=lambda: Role.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])


class DelUserForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])
