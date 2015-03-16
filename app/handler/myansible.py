# -*- coding: utf8 -*-
from ansible.runner import Runner
from tempfile import NamedTemporaryFile
import sys
import tempfile
from ansible.inventory import Inventory
from ansible.inventory.host import Host
from ansible.inventory.group import Group

def ansible(**kwargs):
    results = Runner(
            **kwargs
    ).run()
    return results


def prepare_copy_kwargs(src, dest, hosts=["10.10.32.27"], owner='root', group='root'):
    example_inventory = Inventory(hosts)
    return dict(
        inventory = example_inventory,
        module_name="copy",
        module_args="src=%s dest=%s owner=%s group=%s" % (src, dest, owner, group),
        sudo=True,
    )


def ansible_kwargs(hosts, module_name, module_args,):
    example_inventory = Inventory(hosts)
    return dict(
        inventory = example_inventory,
        module_name=module_name,
        module_args=module_args,
        sudo=True,
    )


def run(hosts, module_name, module_args, ):
    return ansible(**ansible_kwargs(hosts, module_name, module_args, ))


def ansible_save(hosts, content, dest_filepath):
    with NamedTemporaryFile() as tempfile:
        tempfile.write(content)
        tempfile.flush()
        module_name = 'copy'
        module_args = 'src={src} dest={conf_file}'.format(
             src=tempfile.name,
             conf_file=dest_filepath,
        )
        results = run(hosts, module_name, module_args, )
        return results


def ansible_file(hosts, dest_filepath, state):
    module_name = 'file'
    module_args = 'path={path} state={state}'.format(
         path=dest_filepath,
         state=state,
    )
    results = run(hosts, module_name, module_args)
    return results


def ansible_service(hosts, service_name, service_state):
    module_name = 'service'
    module_args = 'name={service_name} state={service_state}'.format(
        service_name=service_name,
        service_state=service_state,
    )
    results = run(hosts, module_name, module_args)
    return results


def ansible_yum(hosts, package_name, state):
    module_name = 'yum'
    module_args = 'name={package_name} state={state}'.format(
        package_name=package_name,
        state=state,
    )
    results = run(hosts, module_name, module_args)
    return results


def ansible_lineinfile(hosts, module_args):
    module_name = 'lineinfile'
    results = run(hosts, module_name, module_args)
    return results


def exist_vip(host, vip):

    result = ansible_lineinfile([host],
        '''dest=/etc/init.d/lvs_realserver regexp="^(SNS_VIP=.*?)(\s*{vip}\s*)(.*)$" line="\\1 \\2\\3" backrefs=yes state=present backup=yes'''.format(vip=vip))
    # 如果文件被修改就是已经存在此vip
    # {'dark': {}, 'contacted': {u'10.10.32.27': {u'msg': u'', 'invocation': {'module_name': 'lineinfile', 'module_args': u'dest=/etc/init.d/lvs_realserver regexp="^(SNS_VIP=.*?)(\\s*10.10.32.111\\s*)(.*)$" line="\x01 \x02\x03" backrefs=yes state=present backup=yes'}, u'changed': False, u'backup': u''}}}
    if 'contacted' in result and result['contacted'] and host in result['contacted']\
            and result['contacted'][host]['changed']:
        return True
    else:
        return False
    import pdb; pdb.set_trace()
    return result


def add_vip(hosts, vip):
    results = []
    for host in hosts:
        result = ansible_yum([host], 'lvsrealserver', 'installed')
        results.append(result)
        if not exist_vip(host, vip):
            result = ansible_service([host], 'lvs_realserver', 'stopped')
            results.append(result)
            result = ansible_lineinfile([host], 
                '''dest=/etc/init.d/lvs_realserver regexp="^(SNS_VIP.*)\\"$" line="\\1 {vip}\\"" backrefs=yes state=present backup=true'''.format(vip=vip))

            results.append(result)
            result = ansible_service([host], 'lvs_realserver', 'started')
            results.append(result)
    import pdb; pdb.set_trace()
    return results


def remove_vip(hosts, vip):
    results = []
    for host in hosts:
        result = ansible_yum([host], 'lvsrealserver', 'installed')
        results.append(result)
        if exist_vip(host, vip):
            result = ansible_service([host], 'lvs_realserver', 'stopped')
            results.append(result)
            result = ansible_lineinfile([host], 
                '''dest=/etc/init.d/lvs_realserver regexp="^(SNS_VIP.*)\s*{vip}\s*(.*\\")$" line="\\1 \\2" backrefs=yes state=present backup=true'''.format(vip=vip))
            results.append(result)
            result = ansible_service([host], 'lvs_realserver', 'started')
            results.append(result)
    import pdb; pdb.set_trace()
    return results


if __name__ == '__main__':
    module_name="copy"

    src = "~/abc"
    dest = "/etc/abc_copys"
    owner = 'wangxulin'
    group = 'root'
    module_args="src=%s dest=%s owner=%s group=%s" % (src, dest, owner, group)

    results = run('10.10.32.25,10.10.32.26'.split(','), module_name, module_args, )

    for k in results.keys():
        for ik in results[k].keys():
            print k, '\t', ik, '\t', results[k][ik]
