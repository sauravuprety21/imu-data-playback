'''
Given CSV data with common header t, ax, ay, az, gx, gy, gz

Feed data, in near real time interval, to a socket

Clean up
1. Read CSV to dataframe
2. Normalize time
3. Create columns with del_ts

Event-loop
1. Send first row
2. Sleep for del_t, then move to next row
'''
import json
import sys
from time import time, sleep
import pandas as pd
from tools.tcp_server import TCPSocketServer


CSV_HEADER = ['time', 'ax', 'ay', 'az', 'gx' 'gy', 'gz']

PATH = sys.argv[0]

DATA_SERVER = TCPSocketServer(11232)
DATA_SERVER.run_thread()

df = pd.read_csv(PATH, names=CSV_HEADER)



def get_time_diffs(i):
    '''
    Returns time difference between given row and the next
    '''
    global df

    if i == (df.shape[1]-1):
        return 0

    t_next = df['time'].loc[i+1]
    return t_next - (df['time'].loc[i])
