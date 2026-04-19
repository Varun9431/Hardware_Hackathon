import time
import math
import board
import busio
from sensors.imu import MotionSensor
from sensors.tof import DistanceSensor
from sensors.peripherals import AlertBuzzer, SystemButton, GimbalServos
from sensors.water import WaterDetector

def main():
    print("--- Initializing Butt Sensor Suite ---")
    
    i2c = busio.I2C(board.SCL, board.SDA)
    
    try:
        print("Starting IMU at 0x6a...")
        imu = MotionSensor(i2c)
        
        print("Starting ToF at 0x29...")
        tof = DistanceSensor(i2c)
        
        print("Initializing Buzzer on GPIO 18...")
        buzzer = AlertBuzzer(pin=18)
        
        print("Initializing Water Sensor on GPIO 23...")
        water = WaterDetector(pin=23)

        print("Initializing Toggle Button on GPIO 24...")
        btn = SystemButton(pin=24)

        print("Initializing Smooth Servos (Cam: 25, ToF: 4)...")
        gimbal = GimbalServos(cam_pin=25, tof_pin=4)
        
    except Exception as e:
        print(f"\nInitialization Error: {e}")
        return

    # --- Button Toggle Logic ---
    button_state = {"is_on": False}

    def toggle_manual_buzzer():
        button_state["is_on"] = not button_state["is_on"]
        
    btn.set_toggle_action(toggle_manual_buzzer)

    # --- Proximity Alarm Variables ---
    MAX_BEEP_DIST = 800.0  # (mm) Distances greater than this will NOT beep
    MIN_BEEP_DIST = 50.0   # (mm) Distance where the beep is at its absolute fastest
    
    last_beep_time = time.time()
    beep_toggle_state = False

    print("\nSystem Live! Press Ctrl+C to stop.")
    print("-" * 115) 

    try:
        while True:
            # Grab Data
            motion = imu.get_reading()
            dist = tof.get_distance()
            wet = water.is_wet()
            btn_active = button_state["is_on"]

            ax, ay, az = motion['accel']
            gx, gy, gz = motion['gyro']

            # Calculate IMU tilt (Pitch)
            pitch = math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2) + 0.001))
            current_imu_angle = pitch 

            # Target Absolute Angles
            CAM_TARGET = 90   
            TOF_TARGET = 120  

            # Raw target calculation (change minus to plus if servos move backwards)
            raw_cam_angle = CAM_TARGET - current_imu_angle
            raw_tof_angle = TOF_TARGET - current_imu_angle

            # Apply Smoothing and Deadband
            actual_cam, actual_tof = gimbal.smooth_update(
                raw_cam_angle, 
                raw_tof_angle, 
                deadband=5.0,    
                smoothing=0.08   # Lowered to 0.08 because the loop runs faster now
            )

            # ==========================================
            # ALARM LOGIC (Master Button -> Water -> ToF)
            # ==========================================
            current_time = time.time()

            if btn_active:
                buzzer.turn_on()
                status = " OVERRIDE"
                
            elif wet:
                buzzer.turn_on()
                status = "!! WET !!"
                
            elif dist <= MAX_BEEP_DIST:
                # 1. Figure out how close we are as a fraction (0.0 to 1.0)
                fraction = (dist - MIN_BEEP_DIST) / (MAX_BEEP_DIST - MIN_BEEP_DIST)
                fraction = max(0.0, min(1.0, fraction)) # Clamp it between 0 and 1
                
                # 2. Map that fraction to a beep delay speed
                # Closer distance = smaller fraction = smaller delay = faster beep
                current_beep_delay = 0.05 + (0.55 * fraction)

                # 3. Toggle the buzzer state if enough time has passed
                if (current_time - last_beep_time) >= current_beep_delay:
                    last_beep_time = current_time
                    beep_toggle_state = not beep_toggle_state
                    
                    if beep_toggle_state:
                        buzzer.turn_on()
                    else:
                        buzzer.turn_off()
                        
                status = " BEEPING "
                
            else:
                buzzer.turn_off()
                beep_toggle_state = False # Reset so the next beep starts ON immediately
                status = "   DRY   "

            # Print Data Stream
            dist_str = f"Dist: {dist:>5.1f}mm"
            gmb_str  = f"Tilt: {current_imu_angle:>5.1f}° | C:{actual_cam:>4.0f}° T:{actual_tof:>4.0f}°"
            
            print(f"{dist_str}  |  {gmb_str}  |  Status: {status}")
            
            # Loop now runs 20 times a second to allow for extremely fast beeping
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nShutting down safely...")
        buzzer.turn_off() 
        print("Re-centering servos...")
        for _ in range(20):
            gimbal.smooth_update(0, 0, deadband=0, smoothing=0.2)
            time.sleep(0.05)

if __name__ == "__main__":
    main()
