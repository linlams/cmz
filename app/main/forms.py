# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField,\
    HiddenField, IntegerField, RadioField
from wtforms.validators import Required
from wtforms import ValidationError
from ..models import Idc, Department, Project, Role, User


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
    name = StringField(u'部门英文缩写(创建后不可修改)', validators=[Required()])
    en_name = StringField(u'部门名称', validators=[Required()])

    def validate_name(self, field):
        if Department.query.filter_by(name=field.name).first():
            raise ValidationError(u'此英文缩写已经存在')


class ProjectForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'项目名称英文缩写(创建后不可修改)', validators=[Required()])
    en_name = StringField(u'项目名称', validators=[Required()])
    department_id = SelectField(u'所属部门', validators=[Required()], choices=DEPARTMENT_CHOICES)

    def validate_name(self, field):
        if Project.query.filter_by(name=field.name).first():
            raise ValidationError(u'此英文缩写已经存在')


class IdcForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'机房名称英文缩写(创建后不可修改)', validators=[Required()])
    en_name = StringField(u'机房名称', validators=[Required()])

    def validate_name(self, field):
        if self.id.data and Idc.query.filter_by(name=field.name).first():
            raise ValidationError(u'此英文缩写已经存在')


class VhostForm(Form):
    id = HiddenField(u'ID')
    idc_id = SelectField(u'IDC机房', validators=[Required()], choices=IDCS_CHOICES)
    ip = StringField(u'VIP', validators=[Required()])


class HostForm(Form):
    id = HiddenField(u'ID')
    idc_id = SelectField(u'IDC机房', validators=[Required()], choices=IDCS_CHOICES)
    ip = StringField(u'IP', validators=[Required()])
    mem_size = IntegerField(u'内存(G)', validators=[Required()])


class RoleForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'角色英文缩写(创建后不可修改)', validators=[Required()])
    en_name = StringField(u'角色名称', validators=[Required()])

    def validate_name(self, field):
        if Role.query.filter_by(name=field.name).first():
            raise ValidationError(u'此英文缩写已经存在')


class UserForm(Form):
    id = HiddenField(u'ID')
    username = StringField(u'用户名(请与统一认证平台一致)', validators=[Required()])
    role_id = SelectField(u'角色', validators=[Required()], choices=ROLE_CHOICES)
    project_id = SelectField(u'所属项目', validators=[Required()], choices=PROJECT_CHOICES)
