import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os

_sensors_count = 5

class Graphic():
    def __init__(self):
        plt.style.use('bmh') 
        self.fig, self.ax = plt.subplots(nrows=_sensors_count+1, ncols=1, figsize=(16, 9), sharex=True)
        self.fig.subplots_adjust(hspace=0.3)

        self.sensor_timestamp = []
        self.sensors_values = {f'S{i}' : [] for i in range(_sensors_count)}
        self.marker_point = np.ones(_sensors_count)*-1
        self.colors = ['forestgreen','brown','dodgerblue','darkorange','darkviolet']
        self.mean_value = None
        self.last_n_values = np.ones(_sensors_count)
        self.mean_values = []
        self.std = []
        self.reseted = False

    def update_list(self,sensor,value):
        self.sensors_values[sensor].append(value)
        self.last_n_values[int(sensor[-1])] = value
        if sensor == 'S0':
            self.mean_value = value
            self.sensor_timestamp.append(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
            return
        self.mean_value += value
        if sensor == f'S{_sensors_count-1}':
            self.mean_values.append(self.mean_value/_sensors_count)
            self.std.append(np.std(self.last_n_values,ddof=1))

    def update_graphic(self, mark_flags = [], update = False):
        if update:
            for s in mark_flags:
                self.marker_point[s] = len(self.sensors_values[f'S{s}'])-1
    
        self.ax[-1].clear()
        self.ax[-1].set_ylabel('Valor')
        for s,ax in enumerate(self.ax[:-1]):
            ax.clear()
            ax.set_ylabel('Valor')
            ax.plot(self.sensors_values[f'S{s}'], color='green')
            self.ax[-1].plot(self.sensors_values[f'S{s}'],linewidth=0.5,color=self.colors[s],label=f'S{s}')
            if self.marker_point[s] != -1:
                ax.axvline(self.marker_point[s],linestyle='--',linewidth=0.5,color='red')
        self.ax[-1].plot(self.mean_values,linewidth=0.7,color='black',
                         label=f'Mean = {round(self.mean_values[-1],2)} | dp = {round(self.std[-1],2)}', marker='.')
        self.ax[-1].legend(fontsize=6,bbox_to_anchor=(1, 1))
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def save_data(self,name=None):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sensors_values['dateTime'] = self.sensor_timestamp
        df = pd.DataFrame(self.sensors_values)
        name = name if name else now
        df.to_csv(os.path.join(root,f'{name}.csv'),sep=';',index=False)
        self.fig.savefig(os.path.join(root,f'{name}.svg'),format='svg')

    def reset(self):
        self.sensor_timestamp = []
        self.sensors_values = {f'S{i}' : [] for i in range(_sensors_count)}
        self.marker_point = np.ones(_sensors_count)*-1
        self.mean_value = None
        self.last_n_values = np.ones(_sensors_count)
        self.mean_values = []
        self.std = []
        self.reseted = True
        for s,ax in enumerate(self.ax):
            ax.clear()
        self.fig.canvas.flush_events()
