# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField,\
    HiddenField, IntegerField, RadioField
from wtforms.validators import Required, IPAddress
from ..models import Keepalived
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
    name = StringField(u'主IP', validators=[Required()])

    idc_id = SelectField(u'IDC机房', validators=[Required()], choices=IDCS_CHOICES)

    ip = StringField(u'主IP', validators=[Required(), IPAddress()])
    back_ip = StringField(u'备IP', validators=[Required(), IPAddress()])

    def validate_ip(self, field):
        if self.id.data:
            mc = Keepalived.query.get(self.id.data)
            if mc.ip != field.data:
                raise ValidationError(u'本实例已经绑定了 %s(%s)' % (field.label.text, mc.ip))
            return

        k = Keepalived.query.filter(or_(ip=field.data, back_ip=field.data)).first()
        if k is not None:
            raise ValidationError(u'%s 已经被绑定.' % (field.data))

    def validate_vhost_id(self, field):
        if self.back_ip.data:
            mc = Keepalived.query.get(self.id.data)
            if mc.back_ip != field.data:
                raise ValidationError(u'本实例已经绑定了 %s(%s)' % (field.label.text, mc.back_ip))
            return

        k = Keepalived.query.filter(or_(ip=field.data, back_ip=field.data)).first()
        if k is not None:
            raise ValidationError(u'%s 已经被绑定' % (field.data))
