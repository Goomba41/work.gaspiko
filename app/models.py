# -*- coding: utf8 -*-
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(32), unique=True)
    photo = db.Column(db.String(50))
    name = db.Column(db.String(15))
    surname = db.Column(db.String(15))
    patronymic = db.Column(db.String(15))
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(12), unique=True)

    birth_date = db.Column(db.Date)
    work_date = db.Column(db.Date)
    last_login = db.Column(db.DateTime)

    status = db.Column(db.SmallInteger)

    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

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
    name = db.Column(db.String(15))

    users = db.relationship('User', backref = 'role',lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r >' % (self.name)
