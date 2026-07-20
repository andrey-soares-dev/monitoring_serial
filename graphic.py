import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os

import requests
import json

from matplotlib.widgets import Button

class Graphic():
    def __init__(self, api_ip, all_sensors=[], plot_sensors=None):
        if plot_sensors is None:
            plot_sensors = all_sensors
        plt.style.use('dark_background') 
        self.fig, self.ax = plt.subplots(nrows=len(plot_sensors)+1, ncols=1, figsize=(16, 9), sharex=True)
        self.fig.subplots_adjust(hspace=0.45, top=0.95, bottom=0.15, left=0.08, right=0.82)
        self.fig.patch.set_facecolor('#1e1e1e')
        for ax in self.ax:
            ax.set_facecolor('#2d2d2d')
            ax.grid(color='#444444', linestyle='--', linewidth=0.5)
        
        self.n_sensors = len(plot_sensors)
        self.plot_sensors = plot_sensors 
        self.all_sensors = all_sensors
        self.sensor_timestamp = []
        self.sensors_values = {f'{i}' : [] for i in self.all_sensors}
        self.marker_point = np.ones(self.n_sensors)*-1
        self.colors = ['#00ff00', '#ff4444', '#00ccff', '#ffaa00', '#ff00ff']
        self.avg_sensors = [s for s in self.plot_sensors if any(c.isdigit() for c in s) and not s.lower().startswith('bme')]
        self.sensor_types = {}
        for s in self.avg_sensors:
            stype = s.split('_')[0] if '_' in s else ''.join([c for c in s if not c.isdigit()])
            if stype not in self.sensor_types:
                self.sensor_types[stype] = []
            self.sensor_types[stype].append(s)
            
        self.last_values = {stype: np.zeros(len(sensors)) for stype, sensors in self.sensor_types.items()}
        self.mean_values = {stype: [] for stype in self.sensor_types}
        self.std_values = {stype: [] for stype in self.sensor_types}
        self.reseted = False
        self.should_reset = False
        self.api_ip = api_ip
        
        ax_botao_gas_injection = self.fig.add_axes([0.65, 0.03, 0.15, 0.06]) 
        self.btn_injection = Button(ax_botao_gas_injection, 'Injeção do Gás', color='#444444', hovercolor='#666666')
        self.btn_injection.label.set_color('white')
        self.btn_injection.label.set_fontweight('bold')
        self.btn_injection.on_clicked(self.ao_clicar_injection)
        self.gas_injection = False
        self.injection_index = 0

        ax_botao = self.fig.add_axes([0.82, 0.03, 0.15, 0.06]) 
        self.btn_salvar = Button(ax_botao, 'Resetar/Salvar Dados', color='#444444', hovercolor='#666666')
        self.btn_salvar.label.set_color('white')
        self.btn_salvar.label.set_fontweight('bold')
        self.btn_salvar.on_clicked(self.ao_clicar_botao)

    def update_list(self,sensor,value,not_skip=True):
        self.sensors_values[sensor].append(value)
        
        if sensor == self.all_sensors[0]:
            self.sensor_timestamp.append(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
            
        if not_skip and sensor in self.avg_sensors:
            stype = sensor.split('_')[0] if '_' in sensor else ''.join([c for c in sensor if not c.isdigit()])
            if stype in self.sensor_types:
                idx = self.sensor_types[stype].index(sensor)
                self.last_values[stype][idx] = value
            
        if self.avg_sensors and sensor == self.avg_sensors[-1]:
            for stype in self.sensor_types:
                current_mean = np.mean(self.last_values[stype])
                self.mean_values[stype].append(current_mean)
                std = np.std(self.last_values[stype], ddof=1) if len(self.last_values[stype]) > 1 else 0
                self.std_values[stype].append(std)

    def update_graphic(self, mark_flags = [], update = False):
        if update:
            for s_name in mark_flags:
                if s_name in self.plot_sensors:
                    idx = self.plot_sensors.index(s_name)
                    self.marker_point[idx] = len(self.sensors_values[s_name]) - 1
    
        self.ax[-1].clear()
        self.ax[-1].set_facecolor('#2d2d2d')
        self.ax[-1].grid(color='#444444', linestyle='--', linewidth=0.5)
        self.ax[-1].set_ylabel('Total', fontweight='bold', fontsize=8)
        self.ax[-1].tick_params(axis='both', which='major', labelsize=8)
        for s,ax in enumerate(self.ax[:-1]):
            s_name = self.plot_sensors[s]
            ax.clear()
            ax.set_facecolor('#2d2d2d')
            ax.grid(color='#444444', linestyle='--', linewidth=0.5)
            ax.set_ylabel(s_name, fontweight='bold', fontsize=8)
            ax.tick_params(axis='both', which='major', labelsize=8)
            
            raw_data = self.sensors_values[s_name]
            current_val = raw_data[-1] if len(raw_data) > 0 else 0
            
            if s_name in self.avg_sensors:
                color_idx = s % len(self.colors)
                self.ax[-1].plot(raw_data,linewidth=1.0,color=self.colors[color_idx],label=f"{s_name} : {current_val}", alpha=0.8)
                ax.plot(raw_data,linewidth=1.5,color=self.colors[color_idx],label=s_name)
            else:
                ax.plot(raw_data,linewidth=1.5,color='#00ff00',label=s_name)
            if self.marker_point[s] != -1:
                ax.axvline(self.marker_point[s],linestyle='--',linewidth=1.0,color='#ff3333')
            if self.gas_injection:
                ax.axvline(self.injection_index,linestyle='--',linewidth=1.0,color='#ffffff')
        
        mean_colors = ['white', 'yellow', 'cyan', '#ffaa00', '#ff00ff']
        for i, stype in enumerate(self.sensor_types):
            if len(self.mean_values[stype]) > 0:
                mean_val = round(self.mean_values[stype][-1], 2)
                std_val = round(self.std_values[stype][-1], 2)
                type_color = mean_colors[i % len(mean_colors)]
                self.ax[-1].plot(self.mean_values[stype], linewidth=2.0, color=type_color,
                                 label=f'{stype.upper()} Média = {mean_val} | DP = {std_val}', marker='', linestyle='-')
        self.ax[-1].legend(fontsize=9, bbox_to_anchor=(0.83, 0.95), bbox_transform=self.fig.transFigure, loc='upper left', frameon=True, facecolor='#2d2d2d', edgecolor='#444444', labelcolor='white')
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
        self.sensors_values = {f'{i}' : [] for i in self.all_sensors}
        self.marker_point = np.ones(self.n_sensors)*-1
        self.last_values = {stype: np.zeros(len(sensors)) for stype, sensors in self.sensor_types.items()}
        self.mean_values = {stype: [] for stype in self.sensor_types}
        self.std_values = {stype: [] for stype in self.sensor_types}
        self.gas_injection = False
        self.injection_index = 0
        self.reseted = True
        for s,ax in enumerate(self.ax):
            ax.clear()
            ax.set_facecolor('#2d2d2d')
            ax.grid(color='#444444', linestyle='--', linewidth=0.5)
        self.fig.canvas.flush_events()

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
        index = len(self.sensors_values[self.all_sensors[0]])
        self.injection_index = index