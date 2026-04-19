from adafruit_lsm6ds.lsm6dsox import LSM6DSOX

class MotionSensor:
    def __init__(self, i2c_bus):
        # We use the shared bus and explicitly set the address from i2cdetect
        self.sensor = LSM6DSOX(i2c_bus, address=0x6A)

    def get_reading(self):
        return {
            "accel": self.sensor.acceleration,
            "gyro": self.sensor.gyro
        }
