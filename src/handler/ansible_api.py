from ansible.runner import Runner
import sys
import tempfile

# args = dict(
#         module_name="copy",
#         module_args="src=%s dest=%s" % (src, dest),
#         )

results = Runner(
    pattern="all",
    module_name='command', module_args='ps -eo pid,command',
    #module_name='command', module_args='/usr/bin/uptime',
).run()

if results is None:
    print "No hosts found"
    sys.exit(1)

print "UP " + "*" * 13

for (hostname, result) in results['contacted'].items():
    if not 'failed' in result:
        #print '%s >>> %s' % (hostname, result['stdout'])
        import re
        pattern = re.compile('^\s*(\d+)\s*(.*memcached.*-p (\d+).*)$', re.MULTILINE)
        all = pattern.findall(result['stdout'])
        print all, hostname
        for a in all:
            result = Runner(
                pattern=hostname,
                module_name='command', module_args='kill -s 15 %s' % a[0],
                sudo=True
            ).run()
            print result


print "FAILED " + "*" * 9

# for (hostname, result) in results['contacted'].items():
#     if 'failed' in result:
#         print '%s >>> %s' % (hostname, result['msg'])
# 
# print "DOWN" + "*" * 9
# 
# for (hostname, result) in results['contacted'].items():
#     print '%s >>> %s' % (hostname, result)


# 
# from pprint import pprint as p
# p(results)
