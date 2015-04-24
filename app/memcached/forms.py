# -*- coding: utf-8 -*-
import urllib2
import re
import json
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField,\
    HiddenField, IntegerField, RadioField
from wtforms.validators import Required, Regexp
from ..models import Memcached, Host
from wtforms import ValidationError


DEPARTMENT_CHOICES = []
PROJECT_CHOICES = []
IDCS_CHOICES = []
VHOST_CHOICES = []
HOST_CHOICES = []
ROLE_CHOICES = []
KEEPALIVEDS_CHOICES = []


class MemcachedForm(Form):
    id = HiddenField(u'ID')
    project_id = SelectField(u'项目', validators=[Required()], choices=PROJECT_CHOICES)

    idc_id = SelectField(u'IDC机房', validators=[Required()], choices=IDCS_CHOICES)
    keepalived_id = SelectField(u'Keepalived名称', validators=[Required()], choices=KEEPALIVEDS_CHOICES)

    vhost_id = SelectField(u'虚拟主机', validators=[Required()], choices=VHOST_CHOICES)
    vhost_port = IntegerField(u'虚拟主机端口', validators=[Required()])

    host_id = SelectField(u'真实主机', validators=[Required()], choices=HOST_CHOICES)
    host_port = IntegerField(u'真实主机端口', validators=[Required()])
    max_mem_size = IntegerField(u'最大内存(MB)', validators=[Required()])
    responsible_persons = StringField(u'负责人(统一认证平台账号,多人用英文逗号分隔)', validators=[Regexp(r'^([A-Za-z0-9_]+)*(\s*,\s*[A-Za-z0-9_]*)*$')])
    users = StringField(u'使用人(统一认证平台账号,多人用英文逗号分隔)', validators=[Regexp(r'^([A-Za-z0-9_]+)*(\s*,\s*[A-Za-z0-9_]*)*$')])

    def validate_vhost_port(self, field):
        if self.id.data:
            mc = Memcached.query.get(self.id.data)
            if mc.vhost_port != field.data:
                raise ValidationError(u'本实例已经绑定了 %s(%s)' % (field.description, mc.vhost_port))
            return

        mc = Memcached.query.filter_by(vhost_port=field.data).first()
        if mc is not None:
            mcs = Memcached.query.all()
            favorable_vhost_port = max(map(lambda x: x.vhost_port, mcs)) + 1
            raise ValidationError(u'%s(%s) 已经被注册. 推荐使用 %s.' % (field.label.text, field.data, favorable_vhost_port))

    def validate_max_mem_size(self, field):
        host = Host.query.get(self.host_id.data)
        available_mem_size = host.mem_size - host.allocated_mem_size(self.id.data)
        if available_mem_size < (int(field.data)/1024.0):
            raise ValidationError(u'%s(%.3fG) 已经使用了%.3fG. 还有%.0fM可用于分配.' % (host.ip, host.mem_size, host.allocated_mem_size(self.id.data), available_mem_size*1024))

    def validate_responsible_persons(self, field):
        spliter = re.compile('\s*,\s*')
        users = spliter.split(field.data)
        for user in users: 
            req = urllib2.Request('https://ksso.kisops.com/manage/api?user=zabbix&password=devops123456!', data="username=%s" % user)
            req.get_method = lambda: 'POST'
            sso_users_str = urllib2.urlopen(req).read()
            users = json.loads(sso_users_str)
            if len(users) == 0:
                raise ValidationError(u'统一认证平台不存在用户:%s' % user)

    def validate_users(self, field):
        self.validate_responsible_persons(field)

