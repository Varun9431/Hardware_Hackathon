from gpiozero import Button, Buzzer
from signal import pause

def main():
    print("--- Buzzer Toggle Test ---")
    
    # Initialize the buzzer on GPIO 18
    # By default, Buzzer class acts as Active High (HIGH = ON)
    buzzer = Buzzer(18)
    
    # Initialize the button on GPIO 24
    # pull_up=True means it triggers when connected to GND
    # bounce_time=0.1 stops physical spring vibrations from causing double-clicks
    button = Button(24, pull_up=True, bounce_time=0.1)

    # gpiozero magic: We directly link the button press to the buzzer's toggle action!
    button.when_pressed = buzzer.toggle

    print("System Live! Press the button to toggle the buzzer.")
    print("Press Ctrl+C to stop.")
    
    try:
        # pause() keeps the script running in the background, listening for the button
        pause()
    except KeyboardInterrupt:
        print("\nShutting down safely...")
        buzzer.off()

if __name__ == "__main__":
    main()
