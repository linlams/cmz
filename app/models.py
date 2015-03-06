# -*- coding: utf-8 -*-
from flask.ext.login import UserMixin
from . import db
from datetime import datetime


class Entity(object):
    removable = db.Column(db.Boolean, nullable=False, default=True)
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    modify_time = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Department(db.Model, Entity):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    projects = db.relationship('Project', backref='department', lazy='dynamic')

    def __repr__(self):
        return '<Department %r>' % self.name


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    memcacheds = db.relationship('Memcached', backref='project', lazy='dynamic')
    members = db.relationship('User', backref='project', lazy='dynamic')

    def __repr__(self):
        return '<Project %r>' % self.name


class Memcached(db.Model):
    __tablename__ = 'memcacheds'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    host_port = db.Column(db.Integer, unique=False)
    max_item_size = db.Column(db.Integer, nullable=False)

    master = db.Column(db.Boolean, nullable=False)

    APPLY_STATUS = 0
    READY_STATUS = 1
    ERROR_STATUS = 2
    status = db.Column(db.Integer, nullable=False, default=0)

    vhost_id = db.Column(db.Integer, db.ForeignKey('vhosts.id'))
    vhost_port = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("host_id", "host_port"),
    )

    def __repr__(self):
        return '<Memcached virtual %r:%r\treal %r:%r>' % (self.vhost.ip, self.vhost_port, self.host.ip, self.host_port)


class Idc(db.Model):
    __tablename__ = 'idcs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    vhosts = db.relationship('Vhost', backref='idc', lazy='dynamic')
    hosts = db.relationship('Host', backref='idc', lazy='dynamic')

    def __repr__(self):
        return '<Idc %r>' % self.name


class Vhost(db.Model):
    __tablename__ = 'vhosts'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True)
    idc_id = db.Column(db.Integer, db.ForeignKey('idcs.id'))
    memcacheds = db.relationship('Memcached', backref='vhost', lazy='dynamic')

    def __repr__(self):
        return '<Vhost %r>' % self.ip


class Host(db.Model):
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True)
    idc_id = db.Column(db.Integer, db.ForeignKey('idcs.id'))
    memcacheds = db.relationship('Memcached', backref='host', lazy='dynamic')

    def __repr__(self):
        return '<Host %r>' % self.ip


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = [
            'User',
            'Administrator',
        ]
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    def __repr__(self):
        return '<User %r>' % self.username


from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
