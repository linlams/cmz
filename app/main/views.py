# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, redirect
from . import main
from .forms import UserForm, DepartmentForm, MemcachedForm, ProjectForm,\
    VhostForm, HostForm, RoleForm, IdcForm

from .. import db
from ..models import User, Role, Department, Memcached, Project, Vhost, Host, Idc


@main.route('/user', methods=['GET', 'POST'])
def user_list():
    form = UserForm()
    form.role_id.choices = [(str(r.id), r.name) for r in Role.query.all()]
    form.project_id.choices = [(str(x.id), x.name) for x in Project.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            user = User.query.get(form.id.data)
        else:
            user = User()

        user.username = form.username.data
        user.role = Role.query.get(form.role_id.data)
        user.project = Project.query.get(form.project_id.data)

        db.session.add(user)
        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('main.user_list'))

    users = User.query.all()
    return render_template('model/user.html',
                           users=users,
                           form=form,)


@main.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    db.session.delete(User.query.get(id))
    return redirect(url_for('main.user_list'))


@main.route('/department', methods=['GET', 'POST'])
def department_list():
    form = DepartmentForm()
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            department = Department.query.get(form.id.data)
        else:
            deployment = Department()

        deployment.name = form.name.data

        db.session.add(department)
        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('main.department_list'))

    departments = Department.query.all()
    return render_template('model/department.html',
                           departments=departments,
                           form=form,)


@main.route('/department/<int:id>', methods=['DELETE'])
def delete_department(id):
    db.session.delete(Department.query.get(id))
    return redirect(url_for('main.department_list'))


@main.route('/project', methods=['GET', 'POST'])
def project_list():
    form = ProjectForm()
    form.department_id.choices = [(str(x.id), x.name) for x in Department.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            project = Project.query.get(form.id.data)
        else:
            project = Project()

        project.name = form.name.data
        project.department = Department.query.get(form.department_id.data)

        db.session.add(project)

        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('main.project_list'))

    projects = Project.query.all()
    return render_template('model/project.html',
                           projects=projects,
                           form=form,)


@main.route('/project/<int:id>', methods=['DELETE'])
def delete_project(id):
    db.session.delete(Project.query.get(id))
    return redirect(url_for('main.project_list'))


@main.route('/host', methods=['GET', 'POST'])
def host_list():
    form = HostForm()
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            host = Host.query.get(form.id.data)
        else:
            host = Host()

        host.idc = Idc.query.get(form.idc_id.data)
        host.ip = form.ip.data

        db.session.add(host)
        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('main.host_list'))

    hosts = Host.query.all()
    return render_template('model/host.html',
                           hosts=hosts,
                           form=form,)


@main.route('/host/<int:id>', methods=['DELETE'])
def delete_host(id):
    db.session.delete(Host.query.get(id))
    return redirect(url_for('main.host_list'))


@main.route('/idc', methods=['GET', 'POST'])
def idc_list():
    form = IdcForm()
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            idc = Idc.query.get(form.id.data)
        else:
            idc = Idc()
        idc.name = form.name.data

        db.session.add(idc)

        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('main.idc_list'))

    idcs = Idc.query.all()
    return render_template('model/idc.html',
                           entities=idcs,
                           entity_type="IDC 信息",
                           form=form,)


@main.route('/vhost', methods=['GET', 'POST'])
def vhost_list():
    form = VhostForm()
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            vhost = Vhost.query.get(form.id.data)
        else:
            vhost = Vhost()

        vhost.idc = Idc.query.get(form.idc_id.data)
        vhost.ip = form.ip.data

        db.session.add(vhost)

        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('main.vhost_list'))

    vhosts = Vhost.query.all()
    return render_template('model/vhost.html',
                           vhosts=vhosts,
                           form=form,)


@main.route('/vhost/<int:id>', methods=['DELETE'])
def delete_vhost(id):
    db.session.delete(Vhost.query.get(id))
    return redirect(url_for('main.vhost_list'))


@main.route('/memcached', methods=['GET', 'POST'])
def memcached_list():
    form = MemcachedForm()
    form.project_id.choices = [(str(x.id), x.name) for x in Project.query.all()]
    form.vhost_id.choices = [(str(x.id), x.ip) for x in Vhost.query.all()]
    form.host_id.choices = [(str(x.id), x.ip) for x in Host.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            mc = Memcached.query.get(form.id.data)
        else:
            mc = Memcached()

        mc.project = Project.query.get(form.project_id.data)
        mc.vhost = Vhost.query.get(form.vhost_id.data)
        mc.host = Host.query.get(form.host_id.data)
        mc.vhost_port = form.vhost_port.data
        mc.host_port = form.host_port.data
        mc.max_item_size = form.max_item_size.data
        mc.master = form.master.data

        db.session.add(mc)
        if form.id.data:
            flash(u'修改成功!')
        else:
            flash(u'保存成功!')
        return redirect(url_for('main.memcached_list'))

    memcacheds = Memcached.query.all()
    return render_template('model/memcached.html',
                           memcacheds=memcacheds,
                           form=form,)


@main.route('/memcached/<int:id>', methods=['DELETE'])
def delete_memcached(id):
    db.session.delete(Memcached.query.get(id))
    return redirect(url_for('main.memcached_list'))
