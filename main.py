from setup import *
import time
import numpy as np
import csv
import os
import signal
import pandas as pd


data_file = 'test.csv'
headers = ['time', 'pressure (Torr)', 'time_in_mm']


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


def save_data(time_hh_mm_ss, pressure, time_in_mm):
    try:
        with open(data_file, 'a') as opf:
            csv_writer = csv.writer(opf, delimiter=',')
            csv_writer.writerow([time_hh_mm_ss, pressure, time_in_mm])
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
        if counter == 0:
            t_0 = time.asctime().split()[3]
            t_0_in_mm = float(t_0.split(':')[0]) * 60 + float(t_0.split(':')[1]) + float(t_0.split(':')[2]) / 60
            save_data(t_0, p, t_0_in_mm)

        else:
            t = time.asctime().split()[3]
            t_0_in_mm = pd.read_csv(data_file)[headers[2]][0]
            t_in_mm = float(t.split(':')[0]) * 60 + float(t.split(':')[1]) + float(t.split(':')[2]) / 60 - t_0_in_mm
            save_data(t, p, t_in_mm)

        counter += 1

        if interrupted:
            print("*******STOP SAVING*******")
            exit()




