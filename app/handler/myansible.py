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
        'dest=/etc/init.d/lvs_realserver regexp="^(SNS_VIP=.*?)\s*{vip}\s*(.*)$" line="\1 {vip}$ \2" backrefs=yes state=present backup=yes'.format(vip=vip))
    import pdb; pdb.set_trace()
    return result


def add_vip(hosts, vip):
    for host in hosts:
        if not exist_vip(host, vip):
            ansible_lineinfile([host], 
                'dest=/etc/init.d/lvs_realserver regexp="^(SNS_VIP.*)\"$" line="\1 {vip}\"" backrefs=yes backup=true'.format(vip=vip))


def remove_vip(hosts, vip):
    for host in hosts:
        if exist_vip(host, vip):
            ansible_lineinfile([host], 
                'dest=/etc/init.d/lvs_realserver regexp="^(SNS_VIP.*)\s*{vip}\s*(.*\")$" line="\1 \2" backrefs=yes backup=true'.format(vip=vip))


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
