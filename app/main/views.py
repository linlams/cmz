# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, redirect
from . import main
from .forms import UserForm, DepartmentForm, ProjectForm,\
    VhostForm, HostForm, IdcForm

from ..handler.myansible import ansible_save, ansible_service, ansible_file, ansible_yum
from .. import db
from ..models import User, Role, Department, Memcached, Project, Vhost, Host, Idc
from flask.ext.login import login_required


@main.route('/', methods=['GET', 'POST'])
def index():
    # return render_template('index.html')
    return redirect(url_for('memcached.index'))


@main.route('/user', methods=['GET', 'POST'])
@login_required
def user_list():
    form = UserForm()
    form.role_id.choices = [(str(r.id), r.name) for r in Role.query.all()]
    # form.project_id.choices = [(str(x.id), x.name) for x in Project.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            user = User.query.get(form.id.data)
        else:
            user = User()

        user.username = form.username.data
        user.role = Role.query.get(form.role_id.data)
        # user.project = Project.query.get(form.project_id.data)

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
@login_required
def delete_user(id):
    db.session.delete(User.query.get(id))
    return redirect(url_for('main.user_list'))


@main.route('/department', methods=['GET', 'POST'])
@login_required
def department_list():
    form = DepartmentForm()
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            department = Department.query.get(form.id.data)
        else:
            department = Department()

        department.code = form.code.data
        department.name = form.name.data

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
@login_required
def delete_department(id):
    db.session.delete(Department.query.get(id))
    return redirect(url_for('main.department_list'))


@main.route('/project', methods=['GET', 'POST'])
@login_required
def project_list():
    form = ProjectForm()
    form.department_id.choices = [(str(x.id), x.name) for x in Department.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            project = Project.query.get(form.id.data)
        else:
            project = Project()

        project.code = form.code.data
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
@login_required
def delete_project(id):
    db.session.delete(Project.query.get(id))
    return redirect(url_for('main.project_list'))


def prepare_zabbix_lld_memcached_script(hosts):
    ansible_yum(hosts, 'zabbix-agent', 'present')

    def ansible_copy(command):
        run(hosts, 'copy', command)

    def ansible_file(command):
        run(hosts, 'file', command)

    dirs = ['/etc/zabbix/zabbix_agentd.conf.d', '/etc/supervisord/conf.d']
    for dir in dirs:
        ansible_file("dest=%s state=directory" % dir)

    files = [
                '/etc/zabbix/zabbix_agentd.conf.d/memcached.conf',
                '/etc/zabbix/script/memcached_discovery.py',
                '/etc/zabbix/script/memcached_status.py',
            ]

    for file in files:
        ansible_copy("src=%s/app/templates%s dest=%s backup=yes" % 
                (current_app.config['BASEDIR'], file, file))

    ansible_service(hosts, 'zabbix_agentd', 'restarted')


@main.route('/host', methods=['GET', 'POST'])
@login_required
def host_list():
    form = HostForm()
    form.idc_id.choices = [(str(x.id), x.name) for x in Idc.query.all()]
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            host = Host.query.get(form.id.data)
        else:
            host = Host()

        host.idc = Idc.query.get(form.idc_id.data)
        host.ip = form.ip.data
        host.mem_size = form.mem_size.data

        db.session.add(host)
        prepare_zabbix_lld_memcached_script([host.ip])
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
@login_required
def delete_host(id):
    db.session.delete(Host.query.get(id))
    return redirect(url_for('main.host_list'))


@main.route('/idc', methods=['GET', 'POST'])
@login_required
def idc_list():
    form = IdcForm()
    form.csrf_enabled = True
    if form.validate_on_submit():
        if form.id.data:
            idc = Idc.query.get(form.id.data)
        else:
            idc = Idc()
        idc.code = form.code.data
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
@login_required
def vhost_list():
    form = VhostForm()
    form.idc_id.choices = [(str(x.id), x.name) for x in Idc.query.all()]
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
@login_required
def delete_vhost(id):
    db.session.delete(Vhost.query.get(id))
    return redirect(url_for('main.vhost_list'))
