echo 1 > /proc/sys/net/ipv6/conf/all/forwarding
ip6tables -I OUTPUT -p icmpv6 --icmpv6-type redirect -j DROP