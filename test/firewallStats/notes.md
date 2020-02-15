Test preparations
=================

* pip3 install mysql.connector --user
* pip3 install pyroute2 --user
* launch proxysql

Setting up network rules
------------------------

* sudo iptables -t nat -A OUTPUT -p tcp -d 192.168.1.70 --dport 6033 -j REDIRECT
* sudo apt-get install sysbench

Launching tests
---------------

* python3 test/firewallStats/firewall_stats_mysql_test.py
