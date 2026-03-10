import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os

_sensors_count = 2

class Graphic():
    def __init__(self):
        plt.style.use('bmh') 
        self.fig, self.ax = plt.subplots(nrows=_sensors_count, ncols=1, figsize=(16, 9), sharex=True)
        self.fig.subplots_adjust(hspace=0.3)

        self.sensor_timestamp = []
        self.sensors_values = {f'S{i}' : [] for i in range(_sensors_count)}
        self.marker_point = np.ones(_sensors_count)*-1

    def update_list(self,sensor,value):
        self.sensors_values[sensor].append(value)
        if sensor == 'S0':
            self.sensor_timestamp.append(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

    def update_graphic(self, mark_flags = [], update = False):
        if update:
            for s in mark_flags:
                self.marker_point[s] = len(self.sensors_values[f'S{s}'])-1
        for s,ax in enumerate(self.ax):
            ax.clear()
            ax.set_ylabel('Valor')
            ax.plot(self.sensors_values[f'S{s}'], color='green')
            if self.marker_point[s] != -1:
                ax.axvline(self.marker_point[s],linestyle='--',linewidth=0.5,color='red')
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def save_data(self):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sensors_values['dateTime'] = self.sensor_timestamp
        df = pd.DataFrame(self.sensors_values)
        df.to_csv(os.path.join(root,'test_codes',f'{now}.csv'),sep=';',index=False)
        self.fig.savefig(os.path.join(root,'test_codes',f'{now}.svg'),format='svg')