# coding:utf8
import datetime
import random
import urllib2
import urllib
import argparse
import string
from conf import settings

KSSO = settings.KSSO


def getData(department, username):
    url = '''https://ksso.ksops.com/manage/api?user=%s&password=%s''' % (KSSO['USERNAME'], KSSO['PASSWORD'])

    data = {
        'department': department,
        'username': username
    }

    return post(url, data)      


def post(url, data):  
    data = urllib.urlencode(data)  
    opener = urllib2.Request(url, data)
    response = urllib2.urlopen(opener)

    res = response.read()
    return res  


def main():
    parser = argparse.ArgumentParser(description='ksso_api', )

    parser.add_argument('-d', action='store', dest='department', default=None,
                        help='department Name')

    parser.add_argument('-u', action='store', dest='username', default=None,
                        help='username')

    result = parser.parse_args()

    department = result.department
    username = result.username
    print result

    data = getData(department, username)
    import json
    data = json.loads(data)
    dd = {}
    for d in map(lambda x: x['department'], data):
        if d in dd:
            dd[d] += 1
        else:
            dd[d] = 1

    for k in dd.keys().sort():
        print k, dd[k]

    print len(data)

    ds = { 
        'CM研发部': 'CM',
        'photogrid产品研发部': 'photogrid',
        '安兔兔产品研发部': 'Antutu',
        '安卓移动': 'Android',
        '测试部': 'QA',
        '测试部-珠海': 'QA-zhuhai',
        '导航产品部': 'navigation',
        '金山毒霸研发部': 'dubadev',
        '金山手机助手': 'kassistant',
        '浏览器': 'brower',
        '平台产品研发部': 'platdev',
        '企业安全': 'ksafty',
        '驱动之家': 'kdriver',
        '商业产品研发部': 'busdev',
        ' 商业效能部': 'busdfc',
        '手机毒霸': 'mduba',
        '移动平台研发部': 'mplatdev',
        '信息部': 'IT',
        '用户体验部': 'ux',
        '游戏技术部': 'gamedev',
        '游戏运营部': 'gamebus',
        '运维部': 'operation',
        '未知': 'unknow',
        '失效': 'useless'
    }

    for k in ds.keys().sort():
        print k, len(json.loads(getData(ds[k], None)))

if __name__ == '__main__':
    main()
