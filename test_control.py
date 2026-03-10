_threshold = 0.0003

class TestControl():

    def __init__(self):
        self.total_steps = 10
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
        