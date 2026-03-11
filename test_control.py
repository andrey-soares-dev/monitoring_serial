_threshold = 0.0003

class HeuristicTestControl():
    def __init__(self):
        self.total_steps = 30
        self.stationary = False
        self.actual_step = 0
        self.last_value_intensity = None
        self.last_value = None
        self.monotony = False

    def check_status(self, value):
        if self.stationary:
            return False
        if self.last_value == None:
            self.last_value = value
            self.last_value_intensity = 1
            return False
        intensity = (value - self.last_value)/self.last_value
        
        last_value = self.last_value
        last_value_intensity = self.last_value_intensity
        self.last_value = value
        self.last_value_intensity = intensity

        if self.monotony and value*last_value > 0:
            self.monotony = last_value_intensity*intensity > 0
            self.actual_step = 0
            return False
        
        self.monotony = last_value_intensity*intensity > 0
        
        if intensity > _threshold:
            self.actual_step = 0
            return False
        
        self.actual_step += 1
        if self.actual_step == self.total_steps:
            self.stationary = True
            return True
        return False
    
class DerivativeControl():
    def __init__(self, epsilon=0.03, total_steps=10, step_size=1):
        self.epsilon = epsilon
        self.total_steps = total_steps
        self.step_size = step_size
        self.stationary = False
        self.actual_step = 0
        self.last_value_intensity = None
        self.last_value = None
    
    def reset(self):
        self.stationary = False
        self.actual_step = 0
        self.last_value_intensity = None
        self.last_value = None

    def check_status(self, value):
        if self.stationary:
            return False
        
        if self.actual_step == 0:
            self.last_value = value
            self.actual_step = 1
            return False
        
        diff = abs(value-self.last_value)/self.step_size
        if diff < self.epsilon:
            self.actual_step += 1
        else:
            self.actual_step = 0
        
        if self.actual_step == 30:
            self.stationary = True
            return True
        return False

import numpy as np
class StandardDeviationControl():
    def __init__(self, cv_stat=0.25, total_steps=30, step_size=1):
        self.cv_stat = cv_stat
        self.total_steps = 30
        self.step_size = step_size
        self.stationary = False
        self.window = []

    def check_status(self, value):
        if self.stationary:
            return False
        
        self.window.append(value)
        if len(self.window) == self.total_steps+1:
            self.window = self.window[1:]
            std = np.std(self.window,ddof=1)
            mean = np.mean(self.window)
            if std/mean < self.cv_stat:
                self.stationary = True
                return True
            return False