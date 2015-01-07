lvs :

memcached 宿主机

memcached 实例

business 业务:



memcached自身状态: (tcp) stats

psutil 获取进程状态:

psutil 宿主机状态:

psutil lvs 状态:

在redis中保存30分钟的状态信息，每分钟（随机(推)取一次数据）


业务 —> lvs(vip:port) --> memcached (ip: port)
业务     lvs               ip 宿主机  port 实例
