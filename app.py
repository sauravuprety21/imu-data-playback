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
import os
from time import time, sleep
import pandas as pd
from tools.tcp_server import TCPSocketServer


CSV_HEADER = ['time', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']

PATH = r"D:\OneDrive - CADIAT\CadiAt\imu\test-records\20220311_0209\sensors"

DATA_SERVER = TCPSocketServer(11232)

df = pd.read_csv(os.path.join(PATH, "acc_gyro.csv"), names=CSV_HEADER, index_col=False)
index_last = df.shape[0] - 1


def get_time_diffs(i):
    '''
    Returns time difference between given row and the next
    '''
    if i < index_last:
        t_next = df['time'].loc[i+1]
        return t_next - (df['time'].loc[i])

    return 0



def send_row(i, t0_clock):
    '''
    Given index of the row, sends IMU values through socket then sleeps.
    '''
    global df, DATA_SERVER

    row = df.loc[i]

    t_clock = time() - t0_clock
    t_row = row['time']

    t_sleep_row = df['time_diff'].loc[i]
    t_throttle = t_clock - t_row
    # correct throttle drift
    t_sleep = t_sleep_row - t_throttle

    # prevent over correction
    if (t_sleep < 0):
        t_sleep = t_sleep_row


    msg = {key: row[key] for key in ['ax', 'ay', 'az', 'gx', 'gy', 'gz']}
    DATA_SERVER.broadcast(json.dumps(msg))

    print(f"[MESSAGE SENT] - \n\tTIME_ROW\t:\t{t_row}\n\tTIME_NOW\t:\t{t_clock}\n\tSLEEPING\t:\t{t_sleep}\n")
    sleep(t_sleep)




if __name__ == "__main__":
    # Normalize time, so start is 0

    t0_data = df['time'].loc[0]
    df['time'] = df['time'] - t0_data

    # Find time diffs between rows (sleep_t)
    df['time_diff'] = df.apply(lambda x: get_time_diffs(x.name), axis=1)

    DATA_SERVER.run_thread()

    print(f"[START] - Starting data playback..")

    t0_clock = time()
    df.apply(lambda x: send_row(x.name, t0_clock), axis=1)
    print(f"[END] - Data playback ended at time - {time()-t0_clock}")
