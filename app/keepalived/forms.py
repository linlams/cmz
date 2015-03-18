# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField,\
    HiddenField, IntegerField, RadioField
from wtforms.validators import Required, IPAddress
from ..models import Keepalived, Idc
from wtforms import ValidationError
from sqlalchemy import or_


DEPARTMENT_CHOICES = []
PROJECT_CHOICES = []
IDCS_CHOICES = []
VHOST_CHOICES = []
HOST_CHOICES = []
ROLE_CHOICES = []


class KeepalivedForm(Form):
    id = HiddenField(u'ID')
    name = StringField(u'名称', validators=[Required()])

    idc_id = SelectField(u'IDC机房', validators=[Required()], choices=IDCS_CHOICES)

    ip = StringField(u'主IP', validators=[Required(), IPAddress()])
    host_interface = StringField(u'主网卡', validators=[Required(), ])

    backup_ip = StringField(u'备IP', validators=[Required(), IPAddress()])
    backup_host_interface = StringField(u'备网卡', validators=[Required(), ])

    def validate_ip(self, field):
        if self.id.data:
            k = Keepalived.query.get(self.id.data)
            if k.ip != field.data:
                raise ValidationError(u'本实例已经绑定了 %s(%s)' % (field.label.text, k.ip))
            return

        k = Keepalived.query.filter(or_(Keepalived.ip==field.data, Keepalived.backup_ip==field.data)).first()
        if k is not None:
            raise ValidationError(u'%s 已经被绑定.' % (field.data))

    def validate_backup_ip(self, field):
        if self.backup_ip.data == self.ip.data:
            raise ValidationError(u'两个IP不能相同')
        if self.id.data:
            k = Keepalived.query.get(self.id.data)
            if k.backup_ip != field.data:
                raise ValidationError(u'本实例已经绑定了 %s(%s)' % (field.label.text, k.backup_ip))
            return

        k = Keepalived.query.filter(or_(Keepalived.ip==field.data, Keepalived.backup_ip==field.data)).first()
        if k is not None:
            raise ValidationError(u'%s 已经被绑定' % (field.data))

    def fill_model(self, k):
        k.code = self.code.data
        k.idc = Idc.query.get(self.idc_id.data)
        k.ip = self.ip.data
        k.host_interface = self.host_interface.data
        k.backup_ip = self.backup_ip.data
        k.backup_host_interface = self.backup_host_interface.data
        return k
