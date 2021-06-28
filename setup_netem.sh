#!/bin/bash
if [ -z $NETDEV ]; then
  NETDEV="eth0"
fi
if [ -z $DELAY_MS ]; then
  DELAY_MS=40
fi
if [ -z $RATE_MBIT ]; then
  RATE_MBIT=100
fi
if [ -z $BUF_PKTS ]; then
  BUF_PKTS=32
fi
if [ -z $LOSS_RATE ]; then
  LOSS_RATE=0
fi

BDP_BYTES=$(echo "($DELAY_MS/1000.0)*($RATE_MBIT*1000000.0/8.0)" | bc -q -l)
BDP_PKTS=$(echo "$BDP_BYTES/1500" | bc -q)
LIMIT_PKTS=$(echo "$BDP_PKTS+$BUF_PKTS" | bc -q)

modprobe ifb
ip link set dev ifb0 up
tc qdisc replace dev ${NETDEV} ingress
tc filter replace dev ${NETDEV} parent ffff: protocol ip u32 match u32 0 0 flowid 1:1 action mirred egress redirect dev ifb0
tc qdisc replace dev ifb0 root netem delay ${DELAY_MS}ms rate ${RATE_MBIT}Mbit limit ${LIMIT_PKTS} loss ${LOSS_RATE}%
