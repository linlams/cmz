from ansible.runner import Runner
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


def ansible_kwargs(module_name, module_args, hosts=["10.10.32.27"]):
    example_inventory = Inventory(hosts)
    return dict(
        inventory = example_inventory,
        module_name=module_name,
        module_args=module_args,
        sudo=True,
    )


def run(module_name, module_args, hosts):
    return ansible(**ansible_kwargs(module_name, module_args, hosts))


if __name__ == '__main__':
    module_name="copy"

    src = "~/abc"
    dest = "/etc/abc_copys"
    owner = 'wangxulin'
    group = 'root'
    module_args="src=%s dest=%s owner=%s group=%s" % (src, dest, owner, group)

    results = run(module_name, module_args, hosts='10.10.32.25,10.10.32.26'.split(','))

    for k in results.keys():
        for ik in results[k].keys():
            print k, '\t', ik, '\t', results[k][ik]
