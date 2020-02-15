import mysql.connector
import unittest
import subprocess

mysqlc = mysql.connector.connect(
    host="localhost",
    user="msandbox",
    passwd="msandbox",
    port="6033"
)

nl_mysqlc = mysql.connector.connect(
    host="192.168.1.70",
    user="msandbox",
    passwd="msandbox",
    port="6033"
)

proxysqlc = mysql.connector.connect(
    host="localhost",
    user="admin",
    passwd="admin",
    port="6032"
)

# Get the IP address of the local interface
local_pip = subprocess.check_output(["hostname", "-I"]).decode().split()[0]

mysql_cursor = mysqlc.cursor(buffered=True)
proxysql_cursor = proxysqlc.cursor(buffered=True)
nl_mysqlc_cursor = nl_mysqlc.cursor(buffered=True)

S_FIREWALL_QUERY = "SELECT * FROM stats_mysql_firewall_digests"
S_FIREWALL_RESET_QUERY = "SELECT * FROM stats_mysql_firewall_digests_reset"
S_DIGESTS_TRACK_HOSTNAME = "SET mysql-query_digests_track_hostname = \"true\""
S_LOAD_MYSQL_VARIABLES = "LOAD MYSQL VARIABLES TO RUNTIME"

class EmptyFirewallDigests(unittest.TestCase):
    def setUp(self):
        # Empty the current firewall stats
        proxysql_cursor.execute(S_FIREWALL_RESET_QUERY)
        proxysql_cursor.execute(S_FIREWALL_RESET_QUERY)
        proxysql_cursor.execute(S_DIGESTS_TRACK_HOSTNAME)
        proxysql_cursor.execute(S_LOAD_MYSQL_VARIABLES)

    def testEmptyFirewallDigests(self):
        if not all(proxysql_cursor):
            self.fail("Table should be empty.")

    def testLocalhostQuery(self):
        mysql_cursor.execute("SHOW DATABASES")
        proxysql_cursor.execute(S_FIREWALL_RESET_QUERY)
        l_result = list(proxysql_cursor)

        if len(l_result) != 1:
            self.fail("Invalid number of elements in stats_mysql_firewall_digests table")

        for (_,_,client_address, digest) in l_result:
            self.assertEqual(client_address, "127.0.0.1")

    def testNonLocalhostQuery(self):
        nl_mysqlc_cursor.execute("SHOW DATABASES")
        proxysql_cursor.execute(S_FIREWALL_RESET_QUERY)
        l_result = list(proxysql_cursor)

        if len(l_result) != 1:
            self.fail("Invalid number of elements in stats_mysql_firewall_digests table")

        for (schemaname, username, client_address, digest) in l_result:
            self.assertEqual(schemaname, "information_schema")
            self.assertEqual(username, "msandbox")
            self.assertEqual(client_address, local_pip)

    def testNonLocalhostQuery(self):
        mysql_cursor.execute("SHOW DATABASES")
        nl_mysqlc_cursor.execute("SHOW DATABASES")

        proxysql_cursor.execute(S_FIREWALL_RESET_QUERY + " ORDER BY client_address")
        l_result = list(proxysql_cursor)

        if len(l_result) != 2:
            self.fail("Invalid number of elements in stats_mysql_firewall_digests table")
        else:
            self.assertEqual(l_result[0][0], "information_schema")
            self.assertEqual(l_result[0][1], "msandbox")
            self.assertEqual(l_result[0][2], local_pip)

            self.assertEqual(l_result[1][0], "information_schema")
            self.assertEqual(l_result[1][1], "msandbox")
            self.assertEqual(l_result[1][2], "127.0.0.1")

    def testSimpleMixedQueries(self):
        proxysql_cursor.execute(S_FIREWALL_RESET_QUERY)
        testbench_command = (
            "sysbench",
            "--report-interval=5",
            "--num-threads=4",
            "--max-time=20",
            "--test=/usr/share/sysbench/oltp_read_only.lua",
            "--mysql-user=msandbox",
            "--mysql-password=msandbox",
            "--mysql-host=127.0.0.1",
            "--mysql-port=6033",
            "run"
        )

        subprocess.call(testbench_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        proxysql_cursor.execute(S_FIREWALL_RESET_QUERY + " ORDER BY client_address")

        l_result = list(proxysql_cursor)
        if len(l_result) != 7:
            self.fail("Invalid number of elements in stats_mysql_firewall_digests table")

if __name__ == "__main__":
    unittest.main() # run all tests