from setup import *
import time
import numpy as np
import csv
import os
import signal
import pandas as pd
from datetime import date
from datetime import datetime


data_file = 'demo3.csv'
headers = ['Date (mm/dd/yy)', 'Time', 'Pressure (Torr)', 'time_in_mm']


class Pressure:
    def __init__(self, logging_time):
        self.t = logging_time

    def setup_logger(self):
        inst.write(cmd_syntax['datalogger start'].encode())
        time.sleep(self.t)
        inst.write(cmd_syntax['datalogger stop'].encode())

    def pressure_readout(self):
        self.setup_logger()
        inst.write(cmd_syntax['download'].encode())
        data = str(inst.readline()).split(r"\r")[1:-1]
        print(data)
        pressure = []
        for i in range(len(data)):
            press = float(data[i].split(';')[1])
            pressure.append(press)
        average_pressure = np.average(pressure)
        return average_pressure


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)
interrupted = False


def diff_dates(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    return abs(d1 - d2).days


def save_data(date, time_hh_mm_ss, pressure, time_in_mm):
    try:
        with open(data_file, 'a') as opf:
            csv_writer = csv.writer(opf, delimiter=',')
            csv_writer.writerow([date, time_hh_mm_ss, pressure, time_in_mm])
    except Exception as ex:
        print("Error:", ex)


if __name__ == '__main__':
    file_exists = os.path.isfile(data_file)
    if not file_exists:
        print('CSV data file initiated.')
        file = open(data_file, 'w')
        writer = csv.writer(file)
        writer.writerow(headers)
        file.close()
    else:
        print('Saving data to existed file.')

    port = find_port()
    inst = MKS_PDR900(port)

    if not file_exists:
        counter = 0
    else:
        counter = 1

    while True:
        pres = Pressure(logging_time=1)
        p = pres.pressure_readout()
        date_today = date.today().strftime("%m/%d/%Y")
        if counter == 0:
            t_0 = time.asctime().split()[3]
            t_0_in_mm = float(t_0.split(':')[0]) * 60 + float(t_0.split(':')[1]) + float(t_0.split(':')[2]) / 60
            save_data(date_today, t_0, p, t_0_in_mm)

        else:
            t = time.asctime().split()[3]
            t_0_in_mm = pd.read_csv(data_file)[headers[3]][0]
            date_start = pd.read_csv(data_file)[headers[0]][0]

            if date_today == date_start:
                t_in_mm = float(t.split(':')[0]) * 60 + float(t.split(':')[1]) + float(t.split(':')[2]) / 60 - t_0_in_mm

            else:
                del_dates = diff_dates(date_start, date_today)
                t_in_mm = float(t.split(':')[0]) * 60 + float(t.split(':')[1]) + float(t.split(':')[2]) / 60 \
                          + (del_dates - 1) * 24 * 60 + (24 * 60 - t_0_in_mm)
            save_data(date_today, t, p, t_in_mm)

        counter += 1

        if interrupted:
            print("*******STOP SAVING*******")
            exit()
