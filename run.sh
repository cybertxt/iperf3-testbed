#!/bin/bash -x
if [ -z $CCA ]; then
  CCA='reno'
fi
if [ -z $TEST_DURATION ]; then
  TEST_DURATION=60
fi

TARGET_HOST='10.10.61.58'

ssh root@${TARGET_HOST} "echo $CCA > /proc/sys/net/ipv4/tcp_congestion_control; iperf3 -sD1"
ping -c ${TEST_DURATION} ${TARGET_HOST} > ping.log&
iperf3 -c ${TARGET_HOST} -R -J -t ${TEST_DURATION} > iperf3.json
sleep 1
grep ttl ping.log | awk '{print $5,$7}' | awk -F'[ =]' '{print $2,$4}' > ping_rtts.log
timestr=`date "+%Y%m%d%H%M"`
python3 iperf3_plotter.py -e 100 -o "iperf3-${CCA}-${TEST_DURATION}-${timestr}" iperf3.json
