# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField,\
    HiddenField, IntegerField, RadioField
from wtforms.validators import Required


DEPARTMENT_CHOICES = []
PROJECT_CHOICES = []
IDCS_CHOICES = []
VHOST_CHOICES = []
HOST_CHOICES = []
ROLE_CHOICES = []
# DEPARTMENT_CHOICES = [(d.id, d.name) for d in Department.query.all()]
# PROJECT_CHOICES = [(p.id, p.name) for p in Project.query.all()]
# VHOST_CHOICES = [(v.id, v.name) for v in Vhost.query.all()]
# HOST_CHOICES = [(h.id, h.name) for h in Host.query.all()]
# ROLE_CHOICES = [(r.id, r.name) for r in Role.query.all()]


class DepartmentForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'部门名称', validators=[Required()])
    submit = SubmitField(u'提交')


class ProjectForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'项目名称', validators=[Required()])
    department_id = SelectField(u'所属部门', validators=[Required()], choices=DEPARTMENT_CHOICES)
    submit = SubmitField(u'提交')


class IdcForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'机房名称', validators=[Required()])


class VhostForm(Form):
    id = HiddenField(u'ID')
    idc_id = SelectField(u'IDC机房', validators=[Required()], choices=IDCS_CHOICES)
    ip = StringField(u'VIP', validators=[Required()])
    submit = SubmitField(u'提交')


class HostForm(Form):
    id = HiddenField(u'ID')
    idc_id = SelectField(u'IDC机房', validators=[Required()], choices=IDCS_CHOICES)
    ip = StringField(u'IP', validators=[Required()])
    submit = SubmitField(u'提交')


class MemcachedForm(Form):
    id = HiddenField(u'ID')
    project_id = SelectField(u'项目', validators=[Required()], choices=PROJECT_CHOICES)

    vhost_id = SelectField(u'虚拟主机', validators=[Required()], choices=VHOST_CHOICES)
    vhost_port = IntegerField(u'虚拟主机端口', validators=[Required()])

    host_id = SelectField(u'真实主机', validators=[Required()], choices=HOST_CHOICES)
    host_port = IntegerField(u'真实主机端口', validators=[Required()])
    max_item_size = IntegerField(u'最大单值(MB)', validators=[Required()])
    master = RadioField(u'主备状态', validators=[Required()], choices=[('0', u'主'), ('1', u'备')])


class RoleForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'角色', validators=[Required()])
    submit = SubmitField(u'提交')


class UserForm(Form):
    id = HiddenField(u'ID')
    username = StringField(u'用户名', validators=[Required()])
    role_id = SelectField(u'角色', validators=[Required()], choices=ROLE_CHOICES)
    project_id = SelectField(u'所属项目', validators=[Required()], choices=PROJECT_CHOICES)
    submit = SubmitField(u'提交')
