import json
import matplotlib.pyplot as plt
import sys
import argparse
import numpy as np
from datetime import datetime


def ema(data, window):
    if len(data) < window + 2:
        return None
    alpha = 2 / float(window + 1)
    ema = []
    for i in range(0, window):
        ema.append(None)
    ema.append(data[window])
    for i in range(window+1, len(data)):
        ema.append(ema[i-1] + alpha*(data[i]-ema[i-1]))
    return ema


def chart(args, data):
    # Setting the default values
    filename = 'iperf3'
    expected_bandwidth = 0
    ema_window = 6
    if args.protocol == 'udp':
        sum_string = 'sum'
    else:
        sum_string = 'sum_sent'
    if args.ema is not None:
        ema_window = int(args.ema)
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
    ax1.set_xlabel('time interval')
    ax1.set_ylabel('Throughput(Mbps)')
    ax1.plot(t, debit, label='Bandwitdh (per second)')
    ax1.axhline(data['end'][sum_string]['bits_per_second']/10**6, color='r', label='Avg bandwidth')
    ax1.axhline(expected_bandwidth, color='g', label='Expected bandwidth')
    #plt.plot(ema(debit, ema_window), label='Bandwidth {} period moving average'.format(ema_window))
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
        
    #rtts = [float(x.strip()) for x in content]
    ax2 = ax1.twinx()
    ax2.set_ylabel('TTL(ms)')
    ax2.plot(t, rtts, color='b', linestyle='dashed', label='RTT')
    fig.legend(loc=4)
    #plt.title('[{}] {}'.format(
    #    data['end']['sender_tcp_congestion'],
    #    datetime.now().strftime('%Y-%m-%d %H:%M')))
        #data['start']['timestamp']['time']))
    #plt.ylabel('bit/s')
    #plt.show()
    plt.savefig(filename+'-with-rtts.pdf')


def be_verbose(args, data):
    print('Version 1.0 - Feb 2019')
    print('Command arguments are {}'.format(args))
    print('Start info : {}'.format(data['start']))
    print('End info : {}'.format(data['end']))


def main(argv):
    parser = argparse.ArgumentParser(description='Simple python iperf JSON data vizualiser. Use -J option with iperf to have a JSON output.')
    parser.add_argument('input', nargs='?', help='JSON output file from iperf')
    parser.add_argument('-a', '--ema', help='Exponential moving average used to smooth the bandwidth. Default at 9.', type=int)
    parser.add_argument('-e', '--expectedbw', help='Expected bandwidth to be plotted in Mb.')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action='store_true')
    parser.add_argument('-l', '--log', help='Plot will be in logarithmic scale', action='store_true')
    parser.add_argument('-o', '--output', help='pdf filename')
    args = parser.parse_args(argv)
    with open(args.input) as f:
        data = json.load(f)
        if args.verbose:
            be_verbose(args, data)
        if data['start']['test_start']['protocol'] == 'UDP':
            args.protocol = 'udp'
        else:
            args.protocol = 'tcp'
        chart(args, data)


if __name__ == '__main__':
    main(sys.argv[1:])
