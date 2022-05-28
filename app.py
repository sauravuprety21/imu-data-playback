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

    if i == (df.shape[i]-1):
        return 0

    t_next = df['time'].loc[i+1]
    return t_next - (df['time'].loc[i])



def send_row(i, t0_clock):
    '''
    Given index of the row, sends IMU values through socket then sleeps.
    '''
    row = df.loc[i]

    t_clock = time() - t0_clock
    t_row = row['time']

    t_sleep = df['time_dff'].loc[i]

    msg = {key: row[key] for key in ['ax', 'ay', 'az', 'gx', 'gy', 'gz']}
    DATA_SERVER.broadcast(json.dumps(msg))

    print(f"[MESSAGE SENT] - \n\tTIME_ROW\t:\t{t_row}\n\tTIME_NOW:\t{t_clock}\n\tSLEEPING:\t{t_sleep}\n")
    print(msg)

    sleep(t_sleep)




if __name__ == "__main__":
    # Normalize time, so start is 0
    t0_data = df['time'].loc[0]
    df['time'] = df['time'] - t0_data

    # Find time diffs between rows (sleep_t)
    df['time_diff'] = df.apply(lambda x: get_time_diffs(x.name), row=1)

    print(f"[START] - Starting data playback..")
    df.apply(lambda x: send_row(x.name, t0_clock), axis=1)
    print(f"[END] - Data playback ended at time - {time.time()-t0_clock}")
