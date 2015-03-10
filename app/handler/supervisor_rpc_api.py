#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xmlrpclib
# from ..conf.settings import db, SUPERVISOR_CONFS_DIR, SUPERVISOR_RPC_URL_TEMPLATE, SUPERVISOR_RPC_KWARGS
SUPERVISOR_RPC_URL_TEMPLATE = 'http://{username}:{password}@{host}:9001/RPC2'
SUPERVISOR_RPC_KWARGS = {
    'username': '',
    'password': '',
    'host': 'localhost',
}

import jinja2
from subprocess import PIPE, Popen
import logging
from supervisor.options import make_namespec, split_namespec
from supervisor import xmlrpc


def process_already_exists(process_name, process_infos):
    return len(filter(lambda x: x['name'] == process_name, process_infos)) == 1


logger = logging.getLogger(__name__)


def src_content(data, template_filepath):
    template_file = open(template_filepath, 'r')
    template = jinja2.Template(template_file.read())

    content = template.render(data)
    return content

filename = '{business_name}_memcached_{vip}_{port}.conf'.format(business_name='', vip='', port='')
dest_filepath = '/etc/supervisord/conf.d/' + filename


class SupervisorController(object):

    def __init__(self, host):

        rpc_kwargs = SUPERVISOR_RPC_KWARGS.copy()
        rpc_kwargs['host'] = host

        server = xmlrpclib.Server(SUPERVISOR_RPC_URL_TEMPLATE.format(**rpc_kwargs))
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

        if "all" in names:
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

    def _startresult(self, result):
        name = make_namespec(result['group'], result['name'])
        code = result['status']
        template = '%s: ERROR (%s)'
        if code == xmlrpc.Faults.BAD_NAME:
            return template % (name, 'no such process')
        elif code == xmlrpc.Faults.NO_FILE:
            return template % (name, 'no such file')
        elif code == xmlrpc.Faults.NOT_EXECUTABLE:
            return template % (name, 'file is not executable')
        elif code == xmlrpc.Faults.ALREADY_STARTED:
            return template % (name, 'already started')
        elif code == xmlrpc.Faults.SPAWN_ERROR:
            return template % (name, 'spawn error')
        elif code == xmlrpc.Faults.ABNORMAL_TERMINATION:
            return template % (name, 'abnormal termination')
        elif code == xmlrpc.Faults.SUCCESS:
            return '%s: started' % name
        # assertion
        raise ValueError('Unknown result code %s for %s' % (code, name))

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
        return self.status(names)

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

        return self.status(names)

    def restart(self, names):
        '''
            restart <name>\t\tRestart a process
            restart <gname>:*\tRestart all processes in a group
            restart <name> <name>\tRestart multiple processes or groups")
            restart all\t\tRestart all processes
            Note: restart does not reread config files.
                For that, see reread and update.
        '''
        self.stop(names)
        return self.start(names)

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

    def avail(self):
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

    def reread(self):
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
                    self.logger.info("ERROR: no such process/group: %s" % name)
                else:
                    raise
            else:
                self.logger.info("%s: removed process group" % name)

    def update(self, gnames):
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
        valid_gnames = gnames

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

        return self.status(gnames)

if __name__ == '__main__':
    host = '10.10.32.25'
    hosts = '10.10.32.25,10.10.32.26,10.10.32.27'.split(',')
    for host in hosts:
        sc = SupervisorController(host)
        print sc.status('all')
        name = sc.status('all')[0]['name']
        print sc.start([name])
