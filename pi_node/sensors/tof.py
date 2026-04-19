import adafruit_vl53l1x

class DistanceSensor:
    def __init__(self, i2c_bus):
        # Initialize the VL53L1X using the shared I2C bus
        self.sensor = adafruit_vl53l1x.VL53L1X(i2c_bus)
        
        # Optional: You can set the timing budget or distance mode here if needed
        # self.sensor.distance_mode = 2 # 1 = Short, 2 = Long

    def get_distance(self):
        # The sensor needs to start ranging, read, then stop
        self.sensor.start_ranging()
        dist_cm = self.sensor.distance
        self.sensor.stop_ranging()
        
        if dist_cm is not None:
            return dist_cm * 10  # Convert cm to mm for consistency
        return -1
