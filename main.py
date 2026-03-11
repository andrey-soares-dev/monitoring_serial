from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from graphic import Graphic
from test_control import HeuristicTestControl,DerivativeControl,StandardDeviationControl
import serial

from serial.tools.list_ports import comports

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
                    if data and 'S0' in data:
                        print("Target value received!")
                        return ser
                    elif data and 'ets' in data:
                        continue
                    elif data and 'S0' not in data:
                        return None
                    if count >= 2:
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
            for i, item in enumerate(values):
                sensor, value = item.split(':')
                value = float(value)
                should_update = test_control[sensor].check_status(value)
                any_update = any_update if any_update else should_update
                if should_update:
                    marks.append(i)
                graphic.update_list(sensor,value)
            graphic.update_graphic(marks,any_update)
                    
    except Exception as ex:
        conn.close()

available_ports = list_serial_ports()
conn = None
for port in available_ports:
    print(port)
    conn = open_serial_port(port)
    if conn is not None:
        print(conn)
        break
n_sensors = 2
test_control = {f'S{i}':DerivativeControl() for i in range(n_sensors)}
graphic = Graphic()
anim = FuncAnimation(graphic.fig,run,cache_frame_data=False)
plt.show()
graphic.save_data()