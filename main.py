from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from graphic import Graphic
from test_control import TestControl
import serial

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
                any_update = should_update
                if should_update:
                    marks.append(i)
                graphic.update_list(sensor,value)
            graphic.update_graphic(marks,any_update)
                    
    except Exception as ex:
        conn.close()


conn = serial.Serial('COM3', 115200)
n_sensors = 2
test_control = {f'S{i}':TestControl() for i in range(n_sensors)}
graphic = Graphic()
anim = FuncAnimation(graphic.fig,run,cache_frame_data=False)
plt.show()
graphic.save_data()