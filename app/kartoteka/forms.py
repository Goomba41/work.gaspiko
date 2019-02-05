# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, DateField, IntegerField, SelectField
from wtforms.validators import Required, regexp, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Kind, Character, Executor, Send, Answer, Admission, User
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import db

class DelExecutorForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])

class AddRequestForm(FlaskForm):
    number = TextField(u'Номер запроса', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=10, message = u'Номер должен быть в диапазоне от 1 до 10 символов')])
    name = TextField(u'Имя', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Имя должно быть в диапазоне от 1 до 15 символов')])
    surname = TextField(u'Фамилия', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=50, message = u'Фамилия должна быть в диапазоне от 1 до 50 символов')])
    patronymic = TextField(u'Отчество', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Отчетсво должна быть в диапазоне от 1 до 15 символов')])
    date_registration = DateField(u'Дата регистрации', id="datepicker-1", validators = [Required(message = u'Поле не может быть пустым')])
    kind_id = QuerySelectField(u'Вид запроса', get_label=lambda x: x.name,  query_factory=lambda: Kind.query.order_by('id'), validators = [Required(message = u'Поле не может быть пустым')])
    admission_id = QuerySelectField(u'Способ поступления', get_label=lambda x: x.name,  query_factory=lambda: Admission.query.order_by('id'), validators = [Required(message = u'Поле не может быть пустым')])
    character_id = QuerySelectField(u'Характер запроса', get_label=lambda x: x.name,  query_factory=lambda: Character.query.order_by('name'), validators = [Required(message = u'Поле не может быть пустым')])
    executor_id = QuerySelectField(u'Исполнитель', get_label=lambda x: x.user.surname+' '+x.user.name+' '+x.user.patronymic, query_factory=lambda: Executor.query.order_by('surname').join(User), validators = [Required(message = u'Поле не может быть пустым')])

class DelRequestForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])


class EditRequestForm(FlaskForm):
    def get_list(X):
        query = X.query.all()
        model_list = []
        for q in query:
            model_list.append((q.id, q.name))
        # print(model_list)
        sorted_list = sorted(model_list, key=lambda tup: tup[1])
        return sorted_list
        # return model_list
    def get_list_executor(X):
        query = X.query.all()
        model_list = []
        for q in query:
            model_list.append((q.id, q.user.surname+' '+q.user.name))
        # print(model_list)
        sorted_list = sorted(model_list, key=lambda tup: tup[1])
        # print(sorted_list)
        return sorted_list
        # return model_list

    number = TextField(u'Номер запроса', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=10, message = u'Номер должен быть в диапазоне от 1 до 10 символов')])
    copies = TextField(u'Количество ксерокопий', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=10, message = u'Количество копий должно быть в диапазоне от 1 до 10 символов')])
    name = TextField(u'Имя ', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Имя должно быть в диапазоне от 1 до 15 символов')])
    surname = TextField(u'Фамилия', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=50, message = u'Фамилия должна быть в диапазоне от 1 до 50 символов')])
    patronymic = TextField(u'Отчество', validators = [Required(message = u'Поле не может быть пустым'), Length(min=1, max=15, message = u'Отчество должно быть в диапазоне от 1 до 15 символов')])
    date_registration = DateField(u'Дата регистрации', id="date_reg", validators = [Required(message = u'Поле не может быть пустым')])
    kind_id = SelectField(u'Вид запроса', coerce=int, choices=get_list(Kind()))
    admission_id = SelectField(u'Способ поступления', coerce=int, choices=get_list(Admission()))
    character_id = SelectField(u'Характер запроса', coerce=int, choices=get_list(Character()))
    executor_id = SelectField(u'Исполнитель', coerce=int, choices=get_list_executor(Executor()))
    send_id = SelectField(u'Способ отправки', coerce=int, choices=get_list(Send()))
    answer_id = SelectField(u'Характер ответа', coerce=int, choices=get_list(Answer()))
    date_done = DateField(u'Дата исполнения', id="date_done", validators=[Optional()])
    date_send = DateField(u'Дата отправки', id="date_send", validators=[Optional()])
    filename = FileField(u'Выберите файл справки', render_kw={'lang': "ru"}, validators = [FileAllowed(['odt', 'doc', 'docx', 'pdf'], u'Только документы в формате *.odt, *.doc, *.docx, *.pdf!')])
