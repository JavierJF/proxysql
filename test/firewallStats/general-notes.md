GENERAL TASK NOTES
==================

Requirements
------------

This sections enumerates the requirements as I understood them:

1. Create a new table in the db called "stats_mysql_firewall_digests".
2. Use the data received by "Query_Processor::update_query_digest" to update a new "umap_query_digest" named "digest_umap2".
3. Use the data in this new "digest_umap2" to fill the table "stats_mysql_firewall_digests" in an analogous way of how it's done for "stats_mysql_query_digest".
4. Verify that implementation is working and data is being written to the table.


Extras
------

This sections enumerates some minor things that I have done extra to the required work:

1. I have implemented "stats_mysql_firewall_digests_reset" functionality, it was not required but it was handy and necessary for testing.
2. I have setup several tests to increase the confidence in the implementation.
3. I have used the same implementation DIGEST_STATS_FAST_THREADS, as in the previous code, was not required, but I didn't almost need to do nothing for using it, so, I went with it.

Thoughts and minor experiment
-----------------------------

I spent some extra time (like 2h really) thinking on why another extra rule I tried for iptables wasn't working:

* sudo iptables -t nat -A OUTPUT -p tcp -d 192.168.1.70 --dport 6033 -j REDIRECT
* sudo iptables -t nat -A INPUT -p tcp -d 127.0.0.1 --dport 6033 -s 10.0.2.15 -j SNAT --to-source X.X.X.X

I tried to use the second rule for being able to fake the source address (ip spoofing) of multiple different clients,
sadly, the rule is not working as expected. Don't know why. The reasoning behind this, is that I was going to write some
tests for seeing how the table was filled, and I thought... well, this is a firewall, I should try to see that source ips
and being recorded properly, and probably in the future will be cool being able to fake multiple incoming connections from
local, and see how the rules and everything performs. Sadly the iptables procedure wasn't working, so my next move, if
I wanted to continue with this, will be writing some minimal proxy in boost::asio, with "boost::asio::basic_raw_socket"
so we can rewrite TCP headers and impersonate any other ips.


Code Improvement
----------------

Now that all the requested and basic functionality has been complemented, I will be doing improvements to the code itself.

1. Create separate "inline" functions to avoid code duplication.
2. Minor improvements in code readability.
3. Change the used class 'QP_query_digest_stats' for a smaller one that suits best it's purpose.
