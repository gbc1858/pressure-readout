from setup import *
import time
import numpy as np
import csv
import os
import signal
import pandas as pd
from datetime import date, datetime


data_file = 'demo4.csv'
headers = ['Date (mm/dd/yy)', 'Time', 'Pressure (Torr)', 'time_in_mm']


class Pressure:
    def __init__(self, instrument, logging_time):
        self.inst = instrument
        self.t = logging_time

    def setup_logger(self):
        """
        Set up the logger for the controller. Pressure data will be saved in the internal memory of the controller as
        the logger being started for the given amount of time.
        :return:
        """
        self.inst.write(cmd_syntax['datalogger start'].encode())
        time.sleep(self.t)
        self.inst.write(cmd_syntax['datalogger stop'].encode())

    def pressure_readout(self):
        """
        After setting up the logger of the controller, pull out the data from the memory.
        :return:
        """
        self.setup_logger()
        self.inst.write(cmd_syntax['download'].encode())
        data = str(self.inst.readline()).split(r"\r")[1:-1]
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
    """
    Find date difference between two given dates.
    :param d1:
    :param d2:
    :return:
    """
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    return abs(d1 - d2).days


def save_data(current_date, time_hh_mm_ss, pressure, time_in_mm):
    """
    Save pressure data.
    :param current_date: date of the acquired data
    :param time_hh_mm_ss: time of the acquired data
    :param pressure: averaged pressure data pulled from the memory
    :param time_in_mm: accumulated time in mm
    :return:
    """
    try:
        with open(data_file, 'a') as opf:
            csv_writer = csv.writer(opf, delimiter=',')
            csv_writer.writerow([current_date, time_hh_mm_ss, pressure, time_in_mm])
    except Exception as ex:
        print("Error:", ex)


def initiate_data_file():
    file_exist = os.path.isfile(data_file)
    if not file_exist:
        print('CSV data file initiated.')
        file = open(data_file, 'w')
        writer = csv.writer(file)
        writer.writerow(headers)
        file.close()
    else:
        print('Saving data to existed file.')
    return file_exist


if __name__ == '__main__':
    file_created = initiate_data_file()
    port = find_port()
    inst = MKS_PDR900(port)

    if not file_created:
        counter = 0
    else:
        counter = 1

    while True:
        pres = Pressure(instrument=inst, logging_time=1)
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
