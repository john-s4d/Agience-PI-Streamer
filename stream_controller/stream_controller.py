import RPi.GPIO as GPIO
import time

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW)

btn1 = False
btn2 = False

# Define callback functions
def button1_callback(channel):
    print("Button 1 pressed")
    global btn1
    if btn1:        
        GPIO.output(23, GPIO.LOW)
        btn1 = False
    else:
        GPIO.output(23, GPIO.HIGH)
        btn1 = True;
    

def button2_callback(channel):
    print("Button 2 pressed")
    global btn2
    if btn2:
        GPIO.output(24, GPIO.LOW)
        btn2 = False
    else:
        GPIO.output(24, GPIO.HIGH)
        btn2 = True

# Register callback functions
GPIO.add_event_detect(22, GPIO.FALLING, callback=button1_callback, bouncetime=200)
GPIO.add_event_detect(27, GPIO.FALLING, callback=button2_callback, bouncetime=200)

# Wait for events
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup() 
    print("Program terminated.")
