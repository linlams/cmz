from pyzabbix import ZabbixAPI, ZabbixAPIException
import re
import sys

ZSERVER = 'http://10.10.15.28:9080/'
zapi = ZabbixAPI(ZSERVER)
zapi.login('wangxulin', 'wangxl123')

def get_triggers():
    unack_triggers = zapi.trigger.get(
        only_true=1,
        skipDependent=1,
        monitored=1,
        active=1,
        expandDescription=1,
        expandExpression=1,
        expandData='host',
        withLastEventUnacknowledged=1,
    )

    def get_problem_mcs_infos(mcs):
        def get_problem_mc_infos(mc):
            mc_trigger_pattern = re.compile(
                    "^Memcached\s{vip}:{vport}\s".format(vip=mc.vhost.ip, vport=mc.vhost_port))

            def _contains(description):
                return mc_trigger_pattern.search(description) is not None

            ts = filter(lambda x: _contains(x['description']), unack_triggers)

            if len(ts):
                return {"memcached": mc.to_json(), "triggers": ts}
            else:
                return None

        return filter(lambda x: bool(x), map(get_problem_mc_infos, mcs))
    return get_problem_mcs_infos(mcs)

