from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from graphic import Graphic
from test_control import HeuristicTestControl, DerivativeControl, StandardDeviationControl
import serial
import sys
from serial.tools.list_ports import comports
from reset_dialog import SaveWindow
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests

ip_port = ''
window = None
conn = None
available_sensors = []
test_control = {}
graphic = None

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
                    if data and not any(skip in data for skip in ['ets ', 'rst:', 'boot:', 'mode:']):
                        if ':' in data and ',' in data:
                            try:
                                parts = data.split(',')
                                sensors = []
                                for p in parts:
                                    if ':' in p:
                                        s_name = p.split(':')[0].strip()
                                        if s_name and s_name != 'ST':
                                            sensors.append(s_name)
                                
                                if len(sensors) > 0:
                                    print(f"Target device identified on {port_name}!")
                                    return ser, sensors
                            except Exception as ex:
                                pass
                    if count >= 15:
                        return None, []
            except Exception as ex:
                return None, []
    except serial.SerialException as e:
        print(f"Skipping {port_name}...")
        return None, []
    return None, []

def run(frame):
    marks = []
    any_update = False
    try:
        if conn and conn.in_waiting > 0:
            line = conn.readline().decode('utf-8').strip()
            values = line.split(',')
            print(line)
            for i, item in enumerate(values):
                try:
                    if graphic.should_reset:
                        int('forçando o erro')
                    
                    if ':' not in item:
                        continue
                        
                    sensor, value = item.split(':')
                    sensor = sensor.strip()
                    
                    if sensor == 'ST' or sensor not in test_control:
                        continue
                        
                    value = float(value)
                    should_update = test_control[sensor].check_status(value)
                    any_update = any_update if any_update else should_update
                    
                    if should_update:
                        marks.append(i)
                        
                    has_digit = any(char.isdigit() for char in sensor)
                    not_skip = has_digit
                        
                    graphic.update_list(sensor, value, not_skip=not_skip)
                    graphic.reseted = False
                    
                except Exception as ex:
                    if not graphic.reseted:
                        save_win = SaveWindow()
                        if save_win.name:
                            graphic.save_data(save_win.name)
                        for t in test_control.keys():
                            test_control[t].reset()
                        graphic.reset()
                        graphic.should_reset = False
                        if conn:
                            conn.reset_input_buffer()
                        return
                        
            graphic.update_graphic(marks, any_update)
                    
    except Exception as ex:
        print('ex:', ex)
        return

available_ports = list_serial_ports()
for port in available_ports:
    print(f"Checking port {port}...")
    conn, available_sensors = open_serial_port(port)
    if conn is not None:
        print(f"Connected to {port} with sensors: {available_sensors}")
        break

if conn is None:
    print("Nenhum dispositivo alvo encontrado nas portas seriais disponíveis.")
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Erro de Conexão", "Nenhum dispositivo válido foi encontrado conectado às portas seriais.")
    sys.exit(0)

test_control = {s: DerivativeControl() for s in available_sensors}

while True:
    def save_port_api():
        global ip_port
        ip_port = ip.get()
        window.quit()
        window.destroy()

    window = tk.Tk()
    window.title("Configuração da API")
    window.configure(bg="#f0f0f0")
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', background="#f0f0f0", font=('Segoe UI', 10))
    style.configure('TButton', font=('Segoe UI', 10))
    style.configure('TEntry', font=('Segoe UI', 10))
    
    width = 320
    height = 160

    width_screen = window.winfo_screenwidth()
    height_screen = window.winfo_screenheight()

    pos_x = (width_screen // 2) - (width // 2)
    pos_y = (height_screen // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    window.attributes('-topmost', True)
    window.config(padx=25, pady=25)

    ip_label = ttk.Label(window, text="Insira o IP/Porta da API:")
    ip_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

    ip = ttk.Entry(window, width=35)
    ip.grid(row=1, column=0, pady=(0, 20), ipady=3)
    ip.focus()

    btn_ok = ttk.Button(window, text="Confirmar", width=15, command=save_port_api)
    btn_ok.grid(row=2, column=0)

    window.mainloop()
    
    print('IP:', ip_port)
    
    try:
        response = requests.get(url=f'http://{ip_port}/callback',
                                headers={'Content-Type': 'application/json'},
                                timeout=5)
        
        if response.status_code == 200:
            print("Sucesso! Status 200.")
            break
        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Aviso", f"A API retornou status {response.status_code}.")
            break

    except requests.exceptions.RequestException as e:
        root = tk.Tk()
        root.withdraw()
        retry = messagebox.askretrycancel("Erro de Conexão", f"Não foi possível conectar à API em http://{ip_port}.\n\nDeseja tentar novamente?")
        if not retry:
            break

graphic = Graphic(ip_port, available_sensors)
anim = FuncAnimation(graphic.fig, run, cache_frame_data=False)
plt.show()

if not graphic.reseted:
    save_win = SaveWindow()
    if save_win.name:
        result = graphic.save_data(save_win.name)
        print(result)

if conn:
    conn.close()