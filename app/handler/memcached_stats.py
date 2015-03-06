#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, telnetlib, sys
import time

class MemcachedStats:

    _client = None
    _key_regex = re.compile(ur'ITEM (.*) \[(.*); (.*)\]')
    _slab_regex = re.compile(ur'STAT items:(.*):number')
    _stat_regex = re.compile(ur"STAT (.*) (.*)\r")
    _pre_stats_with_timestamp = (None, None) # (stats, timestamp)

    def __init__(self, host='localhost', port='11211'):
        self._host = host
        self._port = port

    @property
    def client(self):
        if self._client is None:
            self._client = telnetlib.Telnet(self._host, self._port)
        return self._client

    def command(self, cmd):
        ' Write a command to telnet and return the response '
        self.client.write("%s\n" % cmd)
        return self.client.read_until('END')

    def key_details(self, sort=True, limit=100):
        ' Return a list of tuples containing keys and details '
        cmd = 'stats cachedump %s %s'
        keys = [key for id in self.slab_ids()
            for key in self._key_regex.findall(self.command(cmd % (id, limit)))]
        if sort:
            return sorted(keys)
        else:
            return keys

    def keys(self, sort=True, limit=100):
        ' Return a list of keys in use '
        return [key[0] for key in self.key_details(sort=sort, limit=limit)]

    def slab_ids(self):
        ' Return a list of slab ids in use '
        return self._slab_regex.findall(self.command('stats items'))

    def stats(self):
        ' Return a dict containing memcached stats '
        self._stats_timestamp = time.time()
        return dict(self._stat_regex.findall(self.command('stats')))

    @property
    def curr_connections(self):
        return int(self.stats()['curr_connections'])

    @property
    def hit_rate(self):
        stats = self.stats()
        get_hits = int(stats['get_hits'])
        cmd_get = float(stats['cmd_get'])
        if cmd_get != 0:
            return (get_hits / cmd_get)
        else:
            return 0

    @property
    def memory_usage(self):
        stats = self.stats()
        return int(stats['bytes'])

    @property
    def network_traffic(self):
        pre_stats, pre_timestamp = self._pre_stats_with_timestamp
        curr_stats, curr_timestamp = self.stats(), self._stats_timestamp
        self._pre_stats_with_timestamp = (curr_stats, curr_timestamp)

        if pre_timestamp != None:
            if curr_timestamp != pre_timestamp:
                bytes_read = (int(curr_stats['bytes_read']) - int(pre_stats['bytes_read'])) / 1024.0
                bytes_written = (int(curr_stats['bytes_written']) - int(pre_stats['bytes_written'])) / 1024.0
                time_interval = curr_timestamp - pre_timestamp
                self._pre_network_traffic = (bytes_read / time_interval, bytes_written / time_interval)
            return self._pre_network_traffic
        else:
            return None, None


def main(argv=None):
    if not argv:
        argv = sys.argv
    host = argv[1] if len(argv) >= 2 else '127.0.0.1'
    port = argv[2] if len(argv) >= 3 else '11211'
    import pprint
    m = MemcachedStats(host, port)
    pprint.pprint(m.stats())
    pprint.pprint(m.curr_connections)
    pprint.pprint(m.hit_rate)

if __name__ == '__main__':
    main()
