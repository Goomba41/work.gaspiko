# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import TextField, TextAreaField, PasswordField, DateField, SelectField, BooleanField
from wtforms.validators import Required, regexp, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import Department, Role, Post, User, Table_db
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import TelField

class AddUserForm(FlaskForm):
    login = TextField(u'Логин', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Логин должен быть в диапазоне от 1 до 15 символов')])
    password = PasswordField(u'Пароль', validators = [Required(message = u'Введите пароль'), Length(min=1, message = u'Пароль должен быть более 8 символов')])
    photo = FileField(u'Фото профиля', render_kw={'lang': "ru"}, validators = [FileAllowed(['jpg', 'jpeg', 'png', 'gif'], u'Только изображения!')])
    surname = TextField(u'Фамилия', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Фамилия должна быть в диапазоне от 1 до 15 символов')])
    name= TextField(u'Имя', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Имя должно быть в диапазоне от 1 до 15 символов')])
    patronymic = TextField(u'Отчетство', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Отчество должно быть в диапазоне от 1 до 15 символов')])
    email = TextField(u'Почта', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=50, message = u'Отчество должно быть в диапазоне от 1 до 50 символов')])
    phone = TelField(u'Телефон', validators = [Required(message = u'Поле не может быть пустым')])
    birth_date = DateField(u'Дата рождения', id="datepicker-1", validators = [Required(message = u'Поле не может быть пустым')])
    work_date = DateField(u'В должности с', id="datepicker-2", validators = [Required(message = u'Поле не может быть пустым')])

    department_id = QuerySelectField(u'Отдел', get_label=lambda x: x.name, query_factory=lambda: Department.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])
    post_id = QuerySelectField(u'Должность', get_label=lambda x: x.name,  query_factory=lambda: Post.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])
    role_id = QuerySelectField(u'Роль', get_label=lambda x: x.name,  query_factory=lambda: Role.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])

class EditUserForm(FlaskForm):
    def get_list(X):
        query = X.query.all()
        model_list = []
        for q in query:
            model_list.append((q.id, q.name))
        return model_list

    login = TextField(u'Логин')
    password = PasswordField(u'Пароль')
    photo = FileField(u'Фото профиля', render_kw={'lang': "ru"}, validators = [FileAllowed(['jpg', 'jpeg', 'png', 'gif'], u'Только изображения!')])
    surname = TextField(u'Фамилия', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Фамилия должна быть в диапазоне от 1 до 15 символов')])
    name= TextField(u'Имя', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Имя должно быть в диапазоне от 1 до 15 символов')])
    patronymic = TextField(u'Отчетство', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Отчество должно быть в диапазоне от 1 до 15 символов')])
    email = TextField(u'Почта')
    phone = TelField(u'Телефон')
    birth_date = DateField(u'Дата рождения', id="datepicker-1", validators = [Required(message = u'Поле не может быть пустым')])
    work_date = DateField(u'В должности с', id="datepicker-2", validators = [Required(message = u'Поле не может быть пустым')])

    status = SelectField(u'Вкл./Выкл.', choices=[('1', u'Вкл.'), ('0', u'Выкл.')])

    department_id = SelectField(u'Отдел', coerce=int, choices=get_list(Department()))
    post_id = SelectField(u'Должность', coerce=int, choices=get_list(Post()))
    role_id = SelectField(u'Роль', coerce=int, choices=get_list(Role()))

class DelUserForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])

class AddRoleForm(FlaskForm):
    name = TextField(u'Название', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=50, message = u'Название должно быть в диапазоне от 1 до 50 символов')])

class DelRoleForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])

class AddDepartmentForm(FlaskForm):
    name = TextField(u'Название', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=100, message = u'Название должно быть в диапазоне от 1 до 100 символов')])

class DelDepartmentForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])

class AddPostForm(FlaskForm):
    name = TextField(u'Название', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=100, message = u'Название должно быть в диапазоне от 1 до 100 символов')])

class DelPostForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])

class DelImportantForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])

class DelPermissionForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])

class AddPermissionForm(FlaskForm):
    user_id = QuerySelectField(u'Пользователь', get_label=lambda x: x.surname+' '+x.name+' '+x.patronymic, query_factory=lambda: User.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])
    table_id = QuerySelectField(u'Таблица', get_label=lambda x: x.module_parent.name+' / '+x.name,  query_factory=lambda: Table_db.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])
    enter = BooleanField(u'Доступ', render_kw={'value': 1})
    insert = BooleanField(u'Вставка', render_kw={'value': 1})
    update = BooleanField(u'Изменение', render_kw={'value': 1})
    delete = BooleanField(u'Удаление', render_kw={'value': 1})
