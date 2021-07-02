#!/bin/bash -x
if [ -z $CCA ]; then
  CCA='reno'
fi
if [ -z $TEST_DURATION ]; then
  TEST_DURATION=60
fi

TARGET_HOST='10.10.61.58'
LOCAL_HOST='10.10.28.7'

echo "Begin pulling data from $TARGET_HOST for ${TEST_DURATION}s by using CCA ${CCA}..."

CCA_SAVE=`ssh root@${TARGET_HOST} "cat /proc/sys/net/ipv4/tcp_congestion_control"`
## Start iperf server
ssh root@${TARGET_HOST} "echo $CCA > /proc/sys/net/ipv4/tcp_congestion_control; iperf3 -sD1"
#iperf3 -sD1
## Start ping to record the round-trip-latency
ping -c ${TEST_DURATION} ${TARGET_HOST} > ping.log&
## Do test
#ssh root@${TARGET_HOST} "echo $CCA > /proc/sys/net/ipv4/tcp_congestion_control; iperf3 -c ${LOCAL_HOST} -J -t ${TEST_DURATION}" > iperf3.json
iperf3 -c ${TARGET_HOST} -J -R -t ${TEST_DURATION} > iperf3.json
## Restore the CCA setting
ssh root@${TARGET_HOST} "echo $CCA_SAVE > /proc/sys/net/ipv4/tcp_congestion_control"
## Process the result
grep ttl ping.log | awk '{print $5,$7}' | awk -F'[ =]' '{print $2,$4}' > ping_rtts.log
## Draw graph
timestr=`date "+%Y%m%d%H%M"`
python3 iperf3_plotter.py -e 100 -o "iperf3-${CCA}-${TEST_DURATION}-${timestr}"
