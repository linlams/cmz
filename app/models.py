# -*- coding: utf-8 -*-
import json
from flask import current_app, url_for
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

    def to_json(self):
        dict4json = {
            'url': url_for('api.get_department', id=self.id, _external=True),
            'code': self.code,
            'name': self.name,
            'projects': url_for('api.get_department_projects', id=self.id, _external=True),
        }
        return dict4json

    def __repr__(self):
        return '<Department %r>' % self.name


class Project(db.Model, Entity):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    memcacheds = db.relationship('Memcached', backref='project', lazy='dynamic')
    members = db.relationship('User', backref='project', lazy='dynamic')

    def to_json(self):
        dict4json = {
            'url': url_for('api.get_project', id=self.id, _external=True),
            'code': self.code,
            'name': self.name,
            'department': url_for('api.get_department', id=self.department.id, _external=True),
            'memcacheds': url_for('api.get_project_memcacheds', id=self.id, _external=True),
        }
        return dict4json

    def __repr__(self):
        return '<Project %r>' % self.name


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

    def to_json(self):
        dict4json = {
            'url': url_for('api.get_memcached', id=self.id, _external=True),
            'keepalived': url_for('api.get_keepalived', id=self.keepalived.id, _external=True),
            'project': url_for('api.get_project', id=self.project.id, _external=True),
            'host': url_for('api.get_host', id=self.host.id, _external=True),
            'vhost': url_for('api.get_vhost', id=self.vhost.id, _external=True),
            'host_port': self.host_port,
            'vhost_port': self.vhost_port,
            'max_mem_size': self.max_mem_size,
            'deployed': self.deployed,
            'status': self.status,
        }
        return dict4json

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

    def to_json(self):
        dict4json = {
            'name': self.name,
            'master_ip': self.ip,
            'master_interface': self.host_interface,
            'backup_ip': self.backup_ip,
            'backup_interface': self.backup_host_interface,
            'deployed': self.deployed,
            'status': self.status,
        }

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
        return '<Idc %r>' % self.name


class Vhost(db.Model, Entity):
    __tablename__ = 'vhosts'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True)
    idc_id = db.Column(db.Integer, db.ForeignKey('idcs.id'))
    memcacheds = db.relationship('Memcached', backref='vhost', lazy='dynamic')

    def to_json(self):
        dict4json = {
            'url': url_for('api.get_vhost', id=self.id, _external=True),
            'ip': self.ip,
            #'memcacheds': url_for('api.get_vhost_memcacheds', id=self.id, _external=True),
        }
        return dict4json

    def __repr__(self):
        return '<Vhost %r>' % self.ip


class Host(db.Model, Entity):
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True)
    idc_id = db.Column(db.Integer, db.ForeignKey('idcs.id'))
    mem_size = db.Column(db.Integer)
    status_json = db.Column(db.String(4096))
    memcacheds = db.relationship('Memcached', backref='host', lazy='dynamic')

    def allocated_mem_size(self, mc_id=None):
        allocated = reduce(lambda x, y: x+y,
            map(lambda x: x.max_mem_size,
                filter(lambda x: mc_id in [None, ''] or int(mc_id) != x.id,
                    self.memcacheds
                )
            ), 0
        )/1024.0
        return round(allocated, 3)

    def get_status(self, key):
        status = json.load(self.status_json) if self.status_json else {}
        return status[key] if key in status else None

    def set_status(self, key, value):
        status = json.loads(self.status_json) if self.status_json else {}
        status[key] = value
        self.status_json = json.dumps(status)

    def to_json(self):
        dict4json = {
            'url': url_for('api.get_host', id=self.id, _external=True),
            'ip': self.ip,
            'mem_size': self.mem_size,
            #'memcacheds': url_for('api.get_vhost_memcacheds', id=self.id, _external=True),
        }
        return dict4json

    def __repr__(self):
        return '<Host %r>' % self.ip


class Permission:
    ADMINISTER = 0x80


class Role(db.Model, Entity):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            u'普通用户':('normal', 0x00, True),
            u'管理员':('admin', 0xff, False),
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.code = roles[r][0]
            role.permissions = roles[r][1]
            role.default = roles[r][2]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model, Entity):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    logs = db.relationship('Log', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.username in current_app.config['CACHE_MGR_ADMINS']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def to_json(self):
        dict4json = {
            'username': self.username,
            'role': self.role.code,
        }
        return dict4json

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

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
