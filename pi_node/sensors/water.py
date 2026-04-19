from gpiozero import DigitalInputDevice

class WaterDetector:
    def __init__(self, pin=23):
        # pull_up=False keeps the pin strictly at 0 when dry.
        self.sensor = DigitalInputDevice(pin, pull_up=False)

    def is_wet(self):
        # Returns True if the sensor pushes 3.3V to the pin
        return self.sensor.value == 1
