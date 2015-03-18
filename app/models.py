# -*- coding: utf-8 -*-
from flask.ext.login import UserMixin
from . import db
from datetime import datetime


class Entity(object):
    removable = db.Column(db.Boolean, nullable=False, default=True)
    add_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Department(db.Model, Entity):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64), unique=True)
    projects = db.relationship('Project', backref='department', lazy='dynamic')

    def __repr__(self):
        return '<Department %r>' % self.code


class Project(db.Model, Entity):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    memcacheds = db.relationship('Memcached', backref='project', lazy='dynamic')
    members = db.relationship('User', backref='project', lazy='dynamic')

    def __repr__(self):
        return '<Project %r>' % self.code


class Memcached(db.Model, Entity):
    __tablename__ = 'memcacheds'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    keepalived_id = db.Column(db.Integer, db.ForeignKey('keepaliveds.id'))

    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    host_port = db.Column(db.Integer, unique=False)
    max_mem_size = db.Column(db.Integer, nullable=False)

    vhost_id = db.Column(db.Integer, db.ForeignKey('vhosts.id'))
    vhost_port = db.Column(db.Integer, nullable=False)

    deployed = db.Column(db.Boolean)

    STOPPED_STATUS = 0
    RUNNING_STATUS = 1
    status = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint("host_id", "host_port"),
        db.UniqueConstraint("vhost_id", "vhost_port"),
    )

    def __repr__(self):
        return '<Memcached virtual %r:%r\treal %r:%r>' % (self.vhost.ip, self.vhost_port, self.host.ip, self.host_port)


class Keepalived(db.Model, Entity):
    __tablename__ = 'keepaliveds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    ip = db.Column(db.String(64), unique=True)
    host_interface = db.Column(db.String(64))
    backup_ip = db.Column(db.String(64), unique=True)
    backup_host_interface = db.Column(db.String(64))
    idc_id = db.Column(db.Integer, db.ForeignKey('idcs.id'))
    deployed = db.Column(db.Boolean, default=False)

    STOPPED_STATUS = 0
    RUNNING_STATUS = 1
    status = db.Column(db.Integer, nullable=False, default=0)

    memcacheds = db.relationship('Memcached', backref='keepalived', lazy='dynamic')

    # def __repr__(self):
    #    return '<Keepalived virtual %r:%r\treal %r:%r>' % (self.vhost.ip, self.vhost_port, self.host.ip, self.host_port)


class Idc(db.Model, Entity):
    __tablename__ = 'idcs'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64), unique=True)
    vhosts = db.relationship('Vhost', backref='idc', lazy='dynamic')
    hosts = db.relationship('Host', backref='idc', lazy='dynamic')
    keepaliveds = db.relationship('Keepalived', backref='idc', lazy='dynamic')

    def __repr__(self):
        return '<Idc %r>' % self.code


class Vhost(db.Model, Entity):
    __tablename__ = 'vhosts'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True)
    idc_id = db.Column(db.Integer, db.ForeignKey('idcs.id'))
    memcacheds = db.relationship('Memcached', backref='vhost', lazy='dynamic')

    def __repr__(self):
        return '<Vhost %r>' % self.ip


class Host(db.Model, Entity):
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True)
    idc_id = db.Column(db.Integer, db.ForeignKey('idcs.id'))
    mem_size = db.Column(db.Integer)
    memcacheds = db.relationship('Memcached', backref='host', lazy='dynamic')

    def allocated_mem_size(self, mc_id=None):
        allocated = reduce(lambda x, y: x+y,
            map(lambda x: x.max_mem_size,
                filter(lambda x: mc_id is None or int(mc_id) != x.id,
                    self.memcacheds
                )
            ), 0
        )/1024.0
        return round(allocated, 3)

    def __repr__(self):
        return '<Host %r>' % self.ip


class Role(db.Model, Entity):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
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
        return '<Role %r>' % self.code


class User(UserMixin, db.Model, Entity):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    logs = db.relationship('Log', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username


class Log(db.Model, Entity):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    log_info = db.Column(db.String(4096))

    def __repr__(self):
        return '<User %r>' % self.username


from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
