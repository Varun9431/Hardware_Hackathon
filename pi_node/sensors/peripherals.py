from gpiozero import Button, Buzzer, AngularServo

class AlertBuzzer:
    def __init__(self, pin=18):
        # The standard Buzzer class assumes Active High logic
        self.buzzer = Buzzer(pin)

    def turn_on(self):
        self.buzzer.on()

    def turn_off(self):
        self.buzzer.off()

class SystemButton:
    def __init__(self, pin=24):
        # pull_up=True holds the pin at 3.3V until the button connects it to GND
        # bounce_time=0.1 prevents accidental double-clicks
        self.button = Button(pin, pull_up=True, bounce_time=0.1)

    def set_toggle_action(self, action_function):
        # Tells the Pi to run a specific function the moment the button is pressed
        self.button.when_pressed = action_function

class GimbalServos:
    def __init__(self, cam_pin=25, tof_pin=4):
        # SG90 typical pulse widths are 0.5ms to 2.4ms
        self.cam_servo = AngularServo(
            cam_pin, min_angle=-90, max_angle=90, 
            min_pulse_width=0.0005, max_pulse_width=0.0024
        )
        self.tof_servo = AngularServo(
            tof_pin, min_angle=-90, max_angle=90, 
            min_pulse_width=0.0005, max_pulse_width=0.0024
        )
        
        # State variables for smoothing
        self.current_cam = 0.0
        self.current_tof = 0.0
        self.target_cam = 0.0
        self.target_tof = 0.0

    def smooth_update(self, raw_cam, raw_tof, deadband=5.0, smoothing=0.15):
        # 1. DEADBAND: Only update the target if the raw angle changed enough
        if abs(raw_cam - self.target_cam) > deadband:
            self.target_cam = raw_cam
            
        if abs(raw_tof - self.target_tof) > deadband:
            self.target_tof = raw_tof

        # 2. EASING: Smoothly glide the current angle towards the target angle
        self.current_cam += (self.target_cam - self.current_cam) * smoothing
        self.current_tof += (self.target_tof - self.current_tof) * smoothing

        # 3. CLAMP: Prevent angles from exceeding servo limits
        safe_cam = max(-90, min(90, self.current_cam))
        safe_tof = max(-90, min(90, self.current_tof))
        
        # Apply to hardware
        self.cam_servo.angle = safe_cam
        self.tof_servo.angle = safe_tof
        
        return safe_cam, safe_tof
