# Pressure Readout (from MKS PDR900-1 controller)

## Description
Live plot of pressure versus time will be generated.  The pressure data are obtained from a transducer controller. 

Hardware:
1. Transducer with RS232 interface
2. MKS series 900 controller

## Usage
- In `main.py`, change/verify the name of the data file,
    ~~~~
    data_file = 'demo4.csv'
    ~~~~
- Run `main.py` for data acquiring and saving. Data will be saved in the designated csv file under the following  column headers. 

    | Date (mm/dd/yy) | Time | Pressure (Torr) | time_in_mm |
    |:---------------:|:----:|:---------------:|:----------:|

- Run `live_plot.py` for real-time plot.

