import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os

import requests
from scipy.signal import wiener
import json

from matplotlib.widgets import Button

class Graphic():
    def __init__(self, api_ip, sensors_keys = []):
        plt.style.use('bmh') 
        self.fig, self.ax = plt.subplots(nrows=len(sensors_keys)+1, ncols=1, figsize=(16, 9), sharex=True)
        self.fig.subplots_adjust(hspace=0.3)
        
        self.n_sensors = len(sensors_keys)
        self.sensors_keys = sensors_keys 
        self.sensor_timestamp = []
        self.sensors_values = {f'{i}' : [] for i in self.sensors_keys}
        self.marker_point = np.ones(self.n_sensors)*-1
        self.colors = ['forestgreen','brown','dodgerblue','darkorange','darkviolet']
        self.mean_value = None
        self.last_n_values = np.ones(self.n_sensors-2)
        self.mean_values = []
        self.std = []
        self.reseted = False
        self.should_reset = False
        self.api_ip = api_ip
        
        ax_botao_gas_injection = self.fig.add_axes([0.8, 0.08, 0.1, 0.05]) 
        self.btn_injection = Button(ax_botao_gas_injection, 'Injeção do Gás')
        self.btn_injection.on_clicked(self.ao_clicar_injection)
        self.gas_injection = False
        self.injection_index = 0

        ax_botao = self.fig.add_axes([0.8, 0.02, 0.1, 0.05]) 
        self.btn_salvar = Button(ax_botao, 'Resetar/Salvar Dados')
        self.btn_salvar.on_clicked(self.ao_clicar_botao)

    def update_list(self,sensor,value,not_skip=True):
        self.sensors_values[sensor].append(value)
        if not_skip:
            self.last_n_values[int(sensor[1])-1] = value
        if 'S1' in sensor:
            self.mean_value = value
            self.sensor_timestamp.append(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
            return
        if 'S' in sensor and str.isnumeric(sensor[1]):
            self.mean_value += value
            self.mean_values.append(self.mean_value/(self.n_sensors-2))
            self.std.append(np.std(self.last_n_values,ddof=1))

    def update_graphic(self, mark_flags = [], update = False):
        if update:
            for s in mark_flags:
                self.marker_point[s] = len(self.sensors_values[self.sensors_keys[s]])-1
    
        self.ax[-1].clear()
        self.ax[-1].set_ylabel('Valor')
        for s,ax in enumerate(self.ax[:-1]):
            ax.clear()
            ax.set_ylabel(self.sensors_keys[s])
            ax.plot(self.sensors_values[self.sensors_keys[s]], color='green')
            if 'S' in self.sensors_keys[s]:
                self.ax[-1].plot(self.sensors_values[self.sensors_keys[s]],linewidth=0.5,color=self.colors[s],label=self.sensors_keys[s])
            ax.plot(wiener(self.sensors_values[self.sensors_keys[s]]),linewidth=0.3,color='red',label=self.sensors_keys[s])
            if self.marker_point[s] != -1:
                ax.axvline(self.marker_point[s],linestyle='--',linewidth=0.5,color='red')
            if self.gas_injection:
                ax.axvline(self.injection_index,linestyle='--',linewidth=0.5,color='black')
        self.ax[-1].plot(self.mean_values,linewidth=0.7,color='black',
                         label=f'Mean = {round(self.mean_values[-1],2)} | dp = {round(self.std[-1],2)}', marker='.')
        self.ax[-1].legend(fontsize=6,bbox_to_anchor=(1, 1))
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def save_data(self, name=None):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        if getattr(sys, 'frozen', False):
            root = os.path.dirname(sys.executable)
        else:
            root = os.path.dirname(os.path.abspath(__file__))
        self.sensors_values['dateTime'] = self.sensor_timestamp
        df = pd.DataFrame(self.sensors_values)
        injection_flags = np.zeros(len(df))
        injection_flags[self.injection_index] = 1
        df['Injection'] = injection_flags
        name = name if name else now
        
        csv_path = os.path.join(root, f'{name}.csv')
        svg_path = os.path.join(root, f'{name}.svg')
        df.to_csv(csv_path, sep=';', index=False)
        self.fig.savefig(svg_path, format='svg')
        return self.send_data(df,name)

    def reset(self):
        self.sensor_timestamp = []
        self.sensors_values = {f'{i}' : [] for i in self.sensors_keys}
        self.marker_point = np.ones(self.n_sensors)*-1
        self.mean_value = None
        self.last_n_values = np.ones(self.n_sensors)
        self.mean_values = []
        self.std = []
        self.reseted = True
        for s,ax in enumerate(self.ax):
            ax.clear()
        self.fig.canvas.flush_events()

    def apply_wiener_filter(self):
        fig, ax = plt.subplots(nrows=self.n_sensors+1, ncols=1, figsize=(16, 9), sharex=True)
        fig.subplots_adjust(hspace=0.3)
        ax[-1].clear()
        ax[-1].set_ylabel('Filtered_Value')
        for s,ax in enumerate(ax[:-1]):
            ax.clear()
            ax.set_ylabel('Valor')
            ax.plot(wiener(self.sensors_values[self.sensors_keys[s]]), color='green')
            self.ax[-1].plot(self.sensors_values[self.sensors_keys[s]],linewidth=0.5,color=self.colors[s],label=self.sensors_keys[s])

    def ao_clicar_botao(self, event):
        self.should_reset = True

    def send_data(self, dataset, name):
        payload = json.dumps({'data':dataset.to_dict(orient='records')})
        response = requests.post(url=f'http://{self.api_ip}/send-data/name/{name}',
                                 headers={'Content-Type': 'application/json'},
                                 data=payload)
        return response.status_code == 200
    
    def ao_clicar_injection(self, event):
        self.gas_injection = True
        index = len(self.sensors_values[self.sensors_keys[0]])
        self.injection_index = index