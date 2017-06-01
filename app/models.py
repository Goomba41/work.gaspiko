# -*- coding: utf8 -*-
from app import db
import time

class User(db.Model):
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

    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

    important_news = db.relationship('Important_news', backref = 'user',lazy = 'dynamic')
    history = db.relationship('History', backref = 'user_parent',lazy = 'dynamic')
    permission = db.relationship('Permission', backref = 'user',lazy = 'dynamic')
    news = db.relationship('News', backref = 'user',lazy = 'dynamic')
    appeals = db.relationship('Appeals', backref = 'user',lazy = 'dynamic')

    def __repr__(self):
        return '<Users %r>' % (self.name)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))

    users = db.relationship('User', backref = 'department',lazy = 'dynamic')

    def __repr__(self):
        return '<Department %r >' % (self.name)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    users = db.relationship('User', backref = 'post',lazy = 'dynamic')

    def __repr__(self):
        return '<Post %r >' % (self.name)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    users = db.relationship('User', backref = 'role',lazy = 'dynamic')
    permission = db.relationship('Permission', backref = 'role',lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r >' % (self.name)

class Important_news(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.Text)
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    expired = db.Column(db.DateTime)

    def __repr__(self):
        return '<Good news everyone! %r >' % (self.text)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    url = db.Column(db.String(15))
    comment = db.Column(db.String(50))

    tables = db.relationship('Table', backref = 'module_parent',lazy = 'dynamic')

    def __repr__(self):
        return '<Module! %r >' % (self.name)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    module = db.Column(db.Integer, db.ForeignKey("module.id"))
    name = db.Column(db.String(50))
    url = db.Column(db.String(15))

    history = db.relationship('History', backref = 'table_parent',lazy = 'dynamic')
    permission = db.relationship('Permission', backref = 'table',lazy = 'dynamic')

    def __repr__(self):
        return 'Table %r >' % (self.name)

class History(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    action = db.Column(db.String(50))
    table = db.Column(db.Integer, db.ForeignKey("table.id"))

    def __repr__(self):
        return 'History %r >' % (self.table)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    table_id = db.Column(db.Integer, db.ForeignKey("table.id"))
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    insert = db.Column(db.Boolean)
    update = db.Column(db.Boolean)
    delete = db.Column(db.Boolean)
    enter = db.Column(db.Boolean)

    def __repr__(self):
        return 'Permission %r >' % (self.id)

class News(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    header = db.Column(db.String(255))
    text = db.Column(db.Text)
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    cover = db.Column(db.String(50))

    def __repr__(self):
        return 'News %r >' % (self.id)

class Appeals(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.Text)
    cdate = db.Column(db.DateTime, default=time.strftime("%Y-%m-%d %H:%M:%S"))
    ddate = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger, default=time.strftime("1"))

    def __repr__(self):
        return '<Appeals %r >' % (self.text)
