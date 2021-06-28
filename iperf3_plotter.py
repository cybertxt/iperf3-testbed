import json
import matplotlib.pyplot as plt
import sys
import argparse
import numpy as np
from datetime import datetime

def chart(args, data):
    filename = 'iperf3'
    expected_bandwidth = 0
    sum_string = 'sum_sent'
    if args.expectedbw is not None:
        expected_bandwidth = int(args.expectedbw)
    if args.output is not None:
        filename = args.output

    t = []
    debit = []
    intervals = data['intervals']
    c = 1
    for i in intervals:
        t.append(c)
        debit.append(float(i['sum']['bits_per_second'])/10**6)
        c = c + 1

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Time(s)')
    ax1.set_ylabel('Bandwidth(Mbps)')
    ax1.plot(t, debit, label='Bandwidth(Mbps)')
    ax1.axhline(data['end'][sum_string]['bits_per_second']/10**6, color='r', label='Avg bandwidth')
    ax1.axhline(expected_bandwidth, color='g', label='Expected bandwidth')
    ax1.legend(loc=4)
    plt.title('[{}] {}'.format(
        data['end']['sender_tcp_congestion'],
        datetime.now().strftime('%Y-%m-%d %H:%M')))
    with open('ping_rtts.log') as f:
        lines = f.readlines()
    plt.savefig(filename+'.pdf')
    ax1.get_legend().remove()
    rtts = []
    prev_seq = 0
    for l in lines:
        vals = l.split()
        seq = int(vals[0])
        while seq > prev_seq + 1:
            rtts.append(0)
            prev_seq = prev_seq + 1
        rtts.append(float(vals[1]))
        prev_seq = seq
        
    ax2 = ax1.twinx()
    ax2.set_ylabel('RTT(ms)')
    ax2.plot(t, rtts, color='b', linestyle='dashed', label='RTT')
    fig.legend(loc=4)
    plt.savefig(filename+'-with-rtts.pdf')

def main(argv):
    parser = argparse.ArgumentParser(description='Simple python iperf JSON data vizualiser. Use -J option with iperf to have a JSON output.')
    parser.add_argument('-e', '--expectedbw', help='Expected bandwidth to be plotted in Mb.')
    parser.add_argument('-o', '--output', help='pdf filename')
    args = parser.parse_args(argv)
    with open('iperf3.json') as f:
        data = json.load(f)
    chart(args, data)

if __name__ == '__main__':
    main(sys.argv[1:])
