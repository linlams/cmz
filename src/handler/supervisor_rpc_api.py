#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xmlrpclib
from conf.settings import db, SUPERVISOR_CONFS_DIR
import jinja2
from tempfile import NamedTemporaryFile
from subprocess import PIPE, Popen
import logging


USERNAME = 'user'
PASSWORD = '123'

HOST = '127.0.0.1'
# HOST = '10.10.32.28'

RPC_URL = 'http://{host}:9001/RPC2'.format(host=HOST)

server = xmlrpclib.Server(RPC_URL.format(host=HOST))
process_infos = server.supervisor.getAllProcessInfo()
# server.supervisor.startProcess(pinfo['name'])
# server.supervisor.stopProcess(pinfo['name'])
# server.supervisor.startProcess(process_name)


def process_already_exists(process_name, process_infos):
    return len(filter(lambda x: x['name'] == process_name, process_infos)) == 1


def start_process(process_name, host):
    rpc_url = RPC_URL.format(host=host)
    server = xmlrpclib.Server(rpc_url)
    process_infos = server.supervisor.getAllProcessInfo()

    if process_already_exists(process_name, process_infos):
        raise Exception('Proccess {process_name} already exists'.format(process_name=process_name))

    server.supervisor.startProcess(process_name)

businesses = list(db.business.find())
mcs = list(db.memcached.find())
for business in businesses:
    def _eq_(x):
        return x['ip'] == business['memcached']['ip'] and x['port'] == business['memcached']['port']

    memcached = filter(_eq_, mcs)[0]
    business['memcached'] = memcached


for business in businesses:

    # data
    data = {'businesses': businesses}
    # template
    template_file = open(SUPERVISOR_CONFS_DIR + '/memcached.conf.template', 'r')
    template = jinja2.Template(template_file.read())
    # dest_file
    filename = '%s_memcached_%s_%d.conf' % (business['name'], business['lvs']['vip'], business['lvs']['port'])
    dest_filename = '/etc/supervisord/conf.d/{conf_file}'.format(conf_file=filename)

    def _eq_(x):
        return x['ip'] == business['memcached']['ip'] and x['port'] == business['memcached']['port']

    with NamedTemporaryFile() as tempfile:
        content = template.render(business=business)
        tempfile.write(content)
        tempfile.flush()
        print 'ansible {pattern} -m copy -a "src={src} dest={conf_file}" -s'.format(pattern=business['memcached']['ip'], src=tempfile.name, conf_file=dest_filename)
        p = Popen('ansible {pattern} -m copy -a "src={src} dest={conf_file}" -s'.format(
            pattern=business['memcached']['ip'],
            src=tempfile.name,
            conf_file=dest_filename
        ), stdin=PIPE, stdout=PIPE, shell=True)
        # p = Popen('ansible {pattern} -m command -a "rm {conf_file} -f" -s'.format(
        #     pattern=business['memcached']['ip'],
        #     src=tempfile.name,
        #     conf_file=dest_filename
        # ), stdin=PIPE, stdout=PIPE, shell=True)
        p.wait()
        # print p.stdout.read()


filename = '%s_memcached_%s_%d.conf' % (business['name'], business['lvs']['vip'], business['lvs']['port'])
dest_filename = '/etc/supervisord/conf.d/{conf_file}'.format(conf_file=filename)


logger = logging.getLogger(__name__)


data = {'business': business}
pattern = business['memcached']['ip'],
template_filepath = SUPERVISOR_CONFS_DIR + '/memcached.conf.template'


def template_format(pattern, data, filename, template_filepath, dest_path='/etc/supervisord/conf.d'):
    template_file = open(template_filepath, 'r')
    template = jinja2.Template(template_file.read())

    with NamedTemporaryFile() as tempfile:
        content = template.render(data)
        tempfile.write(content)
        tempfile.flush()
        logger.info(
            'ansible {pattern} -m copy -a "src={src} dest={conf_file}" -s'.format(
                pattern=pattern,
                src=tempfile.name,
                conf_file=dest_path + '/' + filename,
            ))
        p = Popen('ansible {pattern} -m copy -a "src={src} dest={conf_file}" -s'.format(
            pattern=pattern,
            src=tempfile.name,
            conf_file=dest_path + '/' + filename,
        ), stdin=PIPE, stdout=PIPE, shell=True)
        p.wait()


class SupervisorController(object):
    RPC_URL = 'http://{host}:9001/RPC2'.format(host=HOST)

    def __init__(self, host):
        server = xmlrpclib.Server(self.RPC_URL.format(host=host))
        self.supervisor = server.supervisor
        self.logger = logging.getLogger(__name__)

    def status(self, names):
        '''
            status <name>\t\tGet status for a single process
            status <gname>:*\tGet status for all processes in a group
            status <name> <name>\tGet status for multiple named processes
            status\t\t\tGet all process status info
        '''
        all_infos = self.supervisor.getAllProcessInfo()

        if not names or "all" in names:
            matching_infos = all_infos
        else:
            matching_infos = []

            for name in names:
                bad_name = True
                group_name, process_name = split_namespec(name)

                for info in all_infos:
                    matched = info['group'] == group_name
                    if process_name is not None:
                        matched = matched and info['name'] == process_name

                    if matched:
                        bad_name = False
                        matching_infos.append(info)

                if bad_name:
                    if process_name is None:
                        msg = "%s: ERROR (no such group)" % group_name
                    else:
                        msg = "%s: ERROR (no such process)" % name
                    self.logger.info(msg)
        return matching_infos

    def start(self, names):
        '''
            start <name>\t\tStart a process
            start <gname>:*\t\tStart all processes in a group
            start <name> <name>\tStart multiple processes or groups
            start all\t\tStart all processes
        '''

        if not names:
            self.logger.info("Error: start requires a process name")
            return []

        results = []
        if 'all' in names:
            results = self.supervisor.startAllProcesses()
            for result in results:
                result = self._startresult(result)
                self.logger.info(result)

        else:
            for name in names:
                group_name, process_name = split_namespec(name)
                if process_name is None:
                    try:
                        _results = self.supervisor.startProcessGroup(group_name)
                        results.extend(_results)
                        for result in _results:
                            result = self._startresult(result)
                            self.logger.info(result)
                    except xmlrpclib.Fault, e:
                        if e.faultCode == xmlrpc.Faults.BAD_NAME:
                            error = "%s: ERROR (no such group)" % group_name
                            self.logger.info(error)
                        else:
                            raise
                else:
                    try:
                        result = self.supervisor.startProcess(name)
                        results.append(result)
                    except xmlrpclib.Fault, e:
                        error = self._startresult({'status': e.faultCode,
                                                   'name': process_name,
                                                   'group': group_name,
                                                   'description': e.faultString})
                        self.logger.info(error)
                    else:
                        name = make_namespec(group_name, process_name)
                        self.logger.info('%s: started' % name)
        return results

    def stop(self, names):
        '''
            self.logger.info("stop <name>\t\tStop a process")
            self.logger.info("stop <gname>:*\t\tStop all processes in a group")
            self.logger.info("stop <name> <name>\tStop multiple processes or groups")
            self.logger.info("stop all\t\tStop all processes")
        '''

        results = []

        if 'all' in names:
            results = self.supervisor.stopAllProcesses()
            for result in results:
                self.logger.info(result)

        else:
            for name in names:
                group_name, process_name = split_namespec(name)
                if process_name is None:
                    try:
                        _results = self.supervisor.stopProcessGroup(group_name)
                        results.extend(_results)
                        for result in _results:
                            self.logger.info(result)
                    except xmlrpclib.Fault, e:
                        if e.faultCode == xmlrpc.Faults.BAD_NAME:
                            error = "%s: ERROR (no such group)" % group_name
                            self.logger.info(error)
                        else:
                            raise
                else:
                    try:
                        result = self.supervisor.stopProcess(name)
                        results.append(result)
                    except xmlrpclib.Fault, e:
                        error = {
                            'status': e.faultCode,
                            'name': process_name,
                            'group': group_name,
                            'description': e.faultString}
                        results.append(error)
                        self.logger.info(error)
                    else:
                        name = make_namespec(group_name, process_name)
                        self.logger.info('%s: stopped' % name)

    def restart(self, names):
        '''
            restart <name>\t\tRestart a process
            restart <gname>:*\tRestart all processes in a group
            restart <name> <name>\tRestart multiple processes or groups")
            restart all\t\tRestart all processes
            Note: restart does not reread config files.
                For that, see reread and update.
        '''
        self.stop(arg)
        self.start(arg)

    def _formatConfigInfo(self, configinfo):
        name = make_namespec(configinfo['group'], configinfo['name'])
        formatted = {'name': name}
        if configinfo['inuse']:
            formatted['inuse'] = 'in use'
        else:
            formatted['inuse'] = 'avail'
        if configinfo['autostart']:
            formatted['autostart'] = 'auto'
        else:
            formatted['autostart'] = 'manual'
        formatted['priority'] = "%s:%s" % (configinfo['group_prio'],
                                           configinfo['process_prio'])

        template = '%(name)-32s %(inuse)-9s %(autostart)-9s %(priority)s'
        return template % formatted

    def avail(self, arg):
        "avail\t\t\tDisplay all configured processes"
        try:
            configinfo = self.supervisor.getAllConfigInfo()
        except xmlrpclib.Fault, e:
            if e.faultCode == xmlrpc.Faults.SHUTDOWN_STATE:
                self.logger.info('ERROR: self.supervisor shutting down')
            else:
                raise
        else:
            for pinfo in configinfo:
                self.logger.info(self._formatConfigInfo(pinfo))
        return configinfo

    def _formatChanges(self, (added, changed, dropped)):
        changedict = {}
        for n, t in [(added, 'available'),
                     (changed, 'changed'),
                     (dropped, 'disappeared')]:
            changedict.update(dict(zip(n, [t] * len(n))))

        if changedict:
            names = changedict.keys()
            names.sort()
            for name in names:
                self.logger.info("%s: %s" % (name, changedict[name]))
        else:
            self.logger.info("No config updates to processes")

        return {'available': added, 'changed': changed, 'disappeared': dropped}

    def reread(self, arg):
        "reread \t\t\tReload the daemon's configuration files"
        try:
            result = self.supervisor.reloadConfig()
        except xmlrpclib.Fault, e:
            if e.faultCode == xmlrpc.Faults.SHUTDOWN_STATE:
                self.logger.info('ERROR: self.supervisor shutting down')
            elif e.faultCode == xmlrpc.Faults.CANT_REREAD:
                self.logger.info('ERROR: %s' % e.faultString)
            else:
                raise
        else:
            return self._formatChanges(result[0])

    def add(self, names):
        '''
            add <name> [...]\tActivates any updates in config for process/group
        '''
        for name in names:
            try:
                self.supervisor.addProcessGroup(name)
            except xmlrpclib.Fault, e:
                if e.faultCode == xmlrpc.Faults.SHUTDOWN_STATE:
                    self.logger.info('ERROR: shutting down')
                elif e.faultCode == xmlrpc.Faults.ALREADY_ADDED:
                    self.logger.info('ERROR: process group already active')
                elif e.faultCode == xmlrpc.Faults.BAD_NAME:
                    self.logger.info(
                        "ERROR: no such process/group: %s" % name)
                else:
                    raise
            else:
                self.logger.info("%s: added process group" % name)

    def remove(self, names):
        '''
            remove <name> [...]\tRemoves process/group from
            active config
        '''
        for name in names:
            try:
                self.supervisor.removeProcessGroup(name)
            except xmlrpclib.Fault, e:
                if e.faultCode == xmlrpc.Faults.STILL_RUNNING:
                    self.logger.info('ERROR: process/group still running: %s' % name)
                elif e.faultCode == xmlrpc.Faults.BAD_NAME:
                    self.logger.info(
                        "ERROR: no such process/group: %s" % name)
                else:
                    raise
            else:
                self.logger.info("%s: removed process group" % name)

    def update(self, arg):
        '''
            update\t\t\tReload config and add/remove as necessary
            update all\t\tReload config and add/remove as necessary
            update <gname> [...]\tUpdate specific groups
        '''

        def log(name, message):
            self.logger.info("%s: %s" % (name, message))

        try:
            result = self.supervisor.reloadConfig()
        except xmlrpclib.Fault, e:
            if e.faultCode == xmlrpc.Faults.SHUTDOWN_STATE:
                self.logger.info('ERROR: already shutting down')
                return
            else:
                raise

        added, changed, removed = result[0]
        valid_gnames = set(arg.split())

        # If all is specified treat it as if nothing was specified.
        if "all" in valid_gnames:
            valid_gnames = set()

        # If any gnames are specified we need to verify that they are
        # valid in order to print a useful error message.
        if valid_gnames:
            groups = set()
            for info in self.supervisor.getAllProcessInfo():
                groups.add(info['group'])
            # New gnames would not currently exist in this set so
            # add those as well.
            groups.update(added)

            for gname in valid_gnames:
                if gname not in groups:
                    self.logger.info('ERROR: no such group: %s' % gname)

        for gname in removed:
            if valid_gnames and gname not in valid_gnames:
                continue
            results = self.supervisor.stopProcessGroup(gname)
            log(gname, "stopped")

            fails = [res for res in results
                     if res['status'] == xmlrpc.Faults.FAILED]
            if fails:
                log(gname, "has problems; not removing")
                continue
            self.supervisor.removeProcessGroup(gname)
            log(gname, "removed process group")

        for gname in changed:
            if valid_gnames and gname not in valid_gnames:
                continue
            results = self.supervisor.stopProcessGroup(gname)
            log(gname, "stopped")

            self.supervisor.removeProcessGroup(gname)
            self.supervisor.addProcessGroup(gname)
            log(gname, "updated process group")

        for gname in added:
            if valid_gnames and gname not in valid_gnames:
                continue
            self.supervisor.addProcessGroup(gname)
            log(gname, "added process group")
