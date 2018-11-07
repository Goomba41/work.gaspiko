# -*- coding: utf8 -*-
from app import db, ma
import time
from flask import session

class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(32))
    photo = db.Column(db.String(50))
    name = db.Column(db.String(15))
    surname = db.Column(db.String(15))
    patronymic = db.Column(db.String(15))
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(18), unique=True)

    birth_date = db.Column(db.Date)
    work_date = db.Column(db.Date)
    last_login = db.Column(db.DateTime)

    status = db.Column(db.SmallInteger)

    department_id = db.Column(db.Integer, db.ForeignKey("arhiv.department.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("arhiv.post.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("arhiv.role.id"))

    important_news = db.relationship('Important_news', backref = 'user',lazy = 'dynamic')
    history = db.relationship('History', backref = 'user_parent',lazy = 'dynamic')
    permission = db.relationship('Permission', backref = 'user',lazy = 'dynamic')
    news = db.relationship('News', backref = 'user',lazy = 'dynamic')
    appeals = db.relationship('Appeals', backref = 'user',lazy = 'dynamic')
    executor = db.relationship('Executor', backref = 'user',lazy = 'dynamic')
    
    employee = db.relationship('Item', backref = 'item_employee',lazy = 'dynamic', foreign_keys='Item.employee')
    responsible = db.relationship('Item', backref = 'item_responsible',lazy = 'dynamic', foreign_keys='Item.responsible')
    
    def current():
        if session.get('user_id'):
            return User.query.filter(User.id == session['user_id']).first()
        else:
            return None
            
    def can(operation, url):
        user_info = User.current()
        
        table_id = Table_db.query.filter(Table_db.url == url).first().id
        perms = Permission.query.filter(((Permission.role_id==user_info.role_id)|(Permission.user_id==user_info.id))&(Permission.table_id == table_id)).all()


        bool_lst = []
        temp = False

        if operation == "enter":
            for perm in perms:
                bool_lst.append(perm.enter)
        if operation == "insert":
            for perm in perms:
                bool_lst.append(perm.insert)
        if operation == "update":
            for perm in perms:
                bool_lst.append(perm.update)
        if operation == "delete":
            for perm in perms:
                bool_lst.append(perm.delete)

        for boolval in bool_lst:
            temp = temp or boolval
    
        return temp


    def __repr__(self):
        return 'Пользователь id:%i, имя:%r ' % (self.id, self.name)

class Department(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))

    users = db.relationship('User', backref = 'department',lazy = 'dynamic')

    def __repr__(self):
        return 'Отдел %r>' % (self.name)

class Post(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    users = db.relationship('User', backref = 'post',lazy = 'dynamic')

    def __repr__(self):
        return 'Должность %r ' % (self.name)

class Role(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    users = db.relationship('User', backref = 'role',lazy = 'dynamic')
    permission = db.relationship('Permission', backref = 'role',lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r >' % (self.name)

class Important_news(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    author = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))
    text = db.Column(db.Text)
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    expired = db.Column(db.DateTime)

    def __repr__(self):
        return '<Good news everyone! %r >' % (self.text)

class Module(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    url = db.Column(db.String(15))
    comment = db.Column(db.String(50))

    tables = db.relationship('Table_db', backref = 'module_parent',lazy = 'dynamic')

    def __repr__(self):
        return '<Module! %r >' % (self.name)

class Table_db(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    module = db.Column(db.Integer, db.ForeignKey("arhiv.module.id"))
    name = db.Column(db.String(50))
    url = db.Column(db.String(15))

    history = db.relationship('History', backref = 'table_parent',lazy = 'dynamic')
    permission = db.relationship('Permission', backref = 'table',lazy = 'dynamic')

    def __repr__(self):
        return 'Table %r >' % (self.name)

class History(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    action = db.Column(db.String(50))
    table = db.Column(db.Integer, db.ForeignKey("arhiv.table_db.id"))

    def __repr__(self):
        return 'History %r >' % (self.table)

class Permission(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("arhiv.role.id"))
    table_id = db.Column(db.Integer, db.ForeignKey("arhiv.table_db.id"))
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    insert = db.Column(db.Boolean)
    update = db.Column(db.Boolean)
    delete = db.Column(db.Boolean)
    enter = db.Column(db.Boolean)

    def __repr__(self):
        return 'Permission %r >' % (self.id)

class News(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))
    header = db.Column(db.String(255))
    text = db.Column(db.Text)
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    images = db.Column(db.JSON)

    def __repr__(self):
        return 'Новость %r' % (self.id)

class Appeals(db.Model):
    __table_args__ = {'schema': 'arhiv'}
    id = db.Column(db.Integer, primary_key = True)
    author = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))
    text = db.Column(db.Text)
    answer = db.Column(db.Text)
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    ddate = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger, default=time.strftime("1"))

    def __repr__(self):
        return '<Appeals %r >' % (self.text)


class Request(db.Model):
    __bind_key__ = 'kartoteka'
    id = db.Column(db.Integer, primary_key = True)
    number = db.Column(db.String(7))
    copies = db.Column(db.Integer, default = 0)
    name = db.Column(db.String(15))
    surname = db.Column(db.String(50))
    patronymic = db.Column(db.String(15))
    date_registration = db.Column(db.Date, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    kind_id = db.Column(db.Integer, db.ForeignKey("kartoteka.kind.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("kartoteka.admission.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("kartoteka.character.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("kartoteka.executor.id"))
    send_id = db.Column(db.Integer, db.ForeignKey("kartoteka.send.id"))
    answer_id = db.Column(db.Integer, db.ForeignKey("kartoteka.answer.id"))
    date_done = db.Column(db.Date)
    date_send= db.Column(db.Date)

    filename = db.Column(db.String(50))

    def __repr__(self):
        return '<Request %s>' % (self.name)

class Kind(db.Model):
    __bind_key__ = 'kartoteka'
    __table_args__ = {'schema': 'kartoteka'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    request = db.relationship('Request', backref = 'kind',lazy = 'dynamic')

    def __repr__(self):
        return '<Kind %r >' % (self.name)
    
class Admission(db.Model):
    __bind_key__ = 'kartoteka'
    __table_args__ = {'schema': 'kartoteka'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    request = db.relationship('Request', backref = 'admission',lazy = 'dynamic')

    def __repr__(self):
        return '<Admission %r >' % (self.name)

class Character(db.Model):
    __bind_key__ = 'kartoteka'
    __table_args__ = {'schema': 'kartoteka'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    request = db.relationship('Request', backref = 'character',lazy = 'dynamic')

    def __repr__(self):
        return '<Character %r >' % (self.name)

class Send(db.Model):
    __bind_key__ = 'kartoteka'
    __table_args__ = {'schema': 'kartoteka'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    request = db.relationship('Request', backref = 'send',lazy = 'dynamic')

    def __repr__(self):
        return '<Send %r >' % (self.name)

class Answer(db.Model):
    __bind_key__ = 'kartoteka'
    __table_args__ = {'schema': 'kartoteka'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    request = db.relationship('Request', backref = 'answer',lazy = 'dynamic')

    def __repr__(self):
        return '<Answer %r >' % (self.name)

class Executor(db.Model):
    __bind_key__ = 'kartoteka'
    __table_args__ = {'schema': 'kartoteka'}
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))

    request = db.relationship('Request', backref = 'executor',lazy = 'dynamic')

    def __repr__(self):
        return '<Executor %s>' % (self.id)
        

class Item(db.Model):
    __tablename__ = 'items'
    __bind_key__ = 'inventory'
    __table_args__ = {'schema': 'inventory'}
    id = db.Column(db.Integer, primary_key = True)
    
    number = db.Column(db.String(20))
    serial = db.Column(db.String(20))
    
    cdate = db.Column(db.DateTime)
    chdate = db.Column(db.DateTime)
    
    name = db.Column(db.String(100))

    status = db.Column(db.SmallInteger)   
        
    placing = db.Column(db.JSON)
    movements = db.Column(db.JSON)
    
    responsible = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))
    employee = db.Column(db.Integer, db.ForeignKey("arhiv.user.id"))

    def __repr__(self):
        return 'Штучка-дрючка № %i, имя:%r ' % (self.id, self.name)

        
        

#Marshmallow схемы
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        
class RoleSchema(ma.ModelSchema):
    class Meta:
        model = Role
        fields = ('id', 'name')
        
class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post
        fields = ('id', 'name')
        
class UserForNewsSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'surname', 'patronymic', 'login', 'photo', 'post', 'role')
    post = ma.Nested(PostSchema)
    role = ma.Nested(RoleSchema)
    
class NewsSchema(ma.ModelSchema):
    class Meta:
        model = News
    user = ma.Nested(UserForNewsSchema)
    
class ItemSchema(ma.ModelSchema):
    class Meta:
        model = Item
        # fields = ('id', 'email', 'name', 'surname', 'login', 'photo', 'post', 'role')
    item_employee = ma.Nested(UserForNewsSchema)
    item_responsible = ma.Nested(UserForNewsSchema)
