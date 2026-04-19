import board
import busio

def identify_sensor():
    print("Investigating the mysterious 0x29...")
    i2c = busio.I2C(board.SCL, board.SDA)
    
    while not i2c.try_lock():
        pass
        
    try:
        res = bytearray(1)
        
        # Check 1: VL53L0X (Expects 0xee)
        i2c.writeto_then_readfrom(0x29, bytes([0xC0]), res)
        print(f"VL53L0X Check (Reg 0xC0) returned: {hex(res[0])}")
        
        # Check 2: VL6180X (Expects 0xb4)
        i2c.writeto_then_readfrom(0x29, bytes([0x00, 0x00]), res)
        print(f"VL6180X Check (Reg 0x0000) returned: {hex(res[0])}")

        # Check 3: VL53L1X (Expects 0xea)
        i2c.writeto_then_readfrom(0x29, bytes([0x01, 0x0F]), res)
        print(f"VL53L1X Check (Reg 0x010F) returned: {hex(res[0])}")

    except Exception as e:
        print(f"Error reading I2C: {e}")
    finally:
        i2c.unlock()

if __name__ == "__main__":
    identify_sensor()
