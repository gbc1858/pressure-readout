from main import *
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def animate(i):
    data = pd.read_csv(data_file)
    pressure = data[headers[2]]
    t_mm = data[headers[3]]

    ax = plt.gca()
    ax.plot([0] + t_mm[1::].tolist(), [pressure[0]] + pressure[1::].tolist(), 'o-', color='b')
    plt.ylabel('Pressure (Torr)', fontsize=14)
    plt.xlabel('Time (min)', fontsize=14)
    plt.title('Time vs. Pressure' + '\n' + '(Data file: ' + data_file + ')', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(alpha=0.5, ls=':')
    plt.autoscale()


while True:
    ani = FuncAnimation(plt.gcf(), animate, repeat=False, interval=1000)
    plt.tight_layout()
    plt.pause(1)

    # if interrupted:
    #     print("*******QUIT PLOTTING*******")
    #     exit()

