from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from graphic import Graphic
from test_control import HeuristicTestControl,DerivativeControl,StandardDeviationControl
import serial

from serial.tools.list_ports import comports
from reset_dialog import SaveWindow
import tkinter as tk
import requests

ip_port = ''
window = None

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def open_serial_port(port_name, baudrate=115200, timeout=5):
    count = 0
    try:
        ser = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
        if ser.is_open:
            try:
                while True:
                    data = ser.readline().decode(errors='ignore').strip()
                    count += 1
                    print(data)
                    if (data and 'T_BME' in data) or (data and 'CHECKUP' in data) or (data and 'ets' in data) or (data and 'SCD' in data):
                        print("Target value received!")
                        return ser
                    elif data and 'ets' in data:
                        continue
                    elif data and 'T_BME' not in data:
                        return None
                    if count >= 5:
                        return None
            except Exception as ex:
                return None
    except serial.SerialException as e:
        print('Skipping...')
        return None

def run(frame):
    marks = []
    any_update = False
    try:
        if conn.in_waiting > 0:
            line = conn.readline().decode('utf-8').strip()
            values = line.split(',')
            print(line)
            for i, item in enumerate(values):
                try:
                    if graphic.should_reset:
                        int('forçando o erro')
                    sensor, value = item.split(':')
                    if sensor == 'ST':
                        continue
                    value = float(value)
                    should_update = test_control[sensor].check_status(value)
                    any_update = any_update if any_update else should_update
                    if should_update:
                        marks.append(i)
                    not_skip = True
                    try:
                        int(sensor[1])
                    except Exception as ex:
                        not_skip = False
                    graphic.update_list(sensor,value,not_skip=not_skip)
                    graphic.reseted = False
                except Exception as ex:
                    if not graphic.reseted:
                        window = SaveWindow()
                        if window.name:
                            graphic.save_data(window.name)
                        for t in test_control.keys():
                            test_control[t].reset()
                        graphic.reset()
                        graphic.should_reset = False
                        conn.reset_input_buffer()
                        return
            graphic.update_graphic(marks,any_update)
                    
    except Exception as ex:
        print('ex:',ex)
        return


ip_port = ""
n_sensors = "0"

while True:
    def save_port_api():
        global ip_port
        global n_sensors
        ip_port = ip.get()
        n_sensors = entry_sensores.get()
        window.quit()
        window.destroy()

    def numeric_validation(value):
        try:
            int(value)
            return True
        except Exception as ex:
            return False
        
    window = tk.Tk()
    window.title("Configuração da API")
    
    width = 300
    height = 200

    width_screen = window.winfo_screenwidth()
    height_screen = window.winfo_screenheight()

    pos_x = (width_screen // 2) - (width // 2)
    pos_y = (height_screen // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    window.attributes('-topmost', True)
    window.config(padx=20, pady=20)

    ip_label = tk.Label(window, text="Insira o IP:")
    ip_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

    ip = tk.Entry(window, width=30)
    ip.grid(row=1, column=0, columnspan=2, pady=(0, 10))
    ip.focus()

    validation = (window.register(numeric_validation), '%P')
    sensors_label = tk.Label(window, text="Número de sensores:")
    sensors_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))

    entry_sensores = tk.Entry(window, width=30, validate='key', validatecommand=numeric_validation)
    entry_sensores.grid(row=3, column=0, columnspan=2, pady=(0, 15))

    btn_ok = tk.Button(window, text="OK", width=10, command=save_port_api, bg="#e1e1e1")
    btn_ok.grid(row=4, column=0, padx=5)

    window.mainloop()
    
    print('IP:', ip_port)
    print('Sensores:', n_sensors)
    
    try:
        response = requests.get(url=f'http://{ip_port}/callback',
                                headers={'Content-Type': 'application/json'},
                                timeout=5)
        
        if response.status_code == 200:
            print("Sucesso! Status 200.")
            break

    except requests.exceptions.RequestException as e:
        pass

n_sensors = int(n_sensors)
available_ports = list_serial_ports()
conn = None
for port in available_ports:
    print(port)
    conn = open_serial_port(port)
    if conn is not None:
        print(conn)
        break

available_sensors = ['T_BME','H_BME']
specific_sensors = [f'S{i+1}_CO2' for i in range(n_sensors)]
available_sensors.extend(specific_sensors)
test_control = {f'{i}':DerivativeControl() for i in available_sensors}
graphic = Graphic(ip_port, available_sensors)
anim = FuncAnimation(graphic.fig,run,cache_frame_data=False)
plt.show()
if not graphic.reseted:
    window = SaveWindow()
    if window.name:
        result = graphic.save_data(window.name)
        print(result)
conn.close()