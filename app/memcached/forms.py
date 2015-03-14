# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField,\
    HiddenField, IntegerField, RadioField
from wtforms.validators import Required
from ..models import Memcached
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

    def validate_vhost_id(self, field):
        if self.id.data:
            mc = Memcached.query.filter_by(vhost_port=field.data).first()
        #if mc is not None:
