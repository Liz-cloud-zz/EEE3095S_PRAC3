import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import signal
import sys
import time

def main():
    GPIO.setwarnings(False)
    print("setup!")
    GPIO.setmode(GPIO.BCM)
    try:
        # GPIO.setup(23, GPIO.IN)
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(GPIO.input(23))
        print(not GPIO.input(23))
        GPIO.setup([12,13,17,27,22], GPIO.OUT)
        GPIO.add_event_detect(23, GPIO.RISING,callback=btn_increase_pressed, bouncetime=100)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        print("Keyboard interrupt")

    except:
        print("some error") 

    finally:
        print("clean up") 
        GPIO.cleanup() # cleanup all GPIO 
    
def btn_increase_pressed():
    while not GPIO.input(23) == GPIO.LOW:
        GPIO.output([12, 13,17,27,22], GPIO.HIGH)
    print("button was pressed! ")
if __name__ == "__main__":
    main()

# some global variables that need to change as we run the program
# end_of_game = None  # set if the user wins or ends the game

# # DEFINE THE PINS USED HERE
# LED_value = [11, 13, 15]
# LED_accuracy = 32
# btn_submit = 16
# btn_increase = 18
# buzzer = None
# eeprom = ES2EEPROMUtils.ES2EEPROM()
# global pi_pwn
# global guess
# global should_blink
# guess=0
# should_blink=False
# global username

# #use the signal module to be able to handle and make the program pause indefinitely.
# def signal_handler(sig, frame):
#     GPIO.cleanup()
#     sys.exit(0)

# # Setup Pins
# def setup():
#     # Setup board mode
#     GPIO.setmode(GPIO.BOARD)

#     # Setup regular GPIO:
#     # Set LEDS for outputs 
#     for i in range (len(LED_value)):
#         GPIO.setup(LED_value[i], GPIO.OUTPUT) # set GPIO pins as input  
#     GPIO.set(LED_accuracy,GPIO.OUTPUT)
#     # Set buttons for input
#     GPIO.setup(btn_increase,GPIO.IN,pull_up=GPIO.PUD_UP)
#     GPIO.setup(btn_submit,GPIO.IN,pull_up=GPIO.PUD_UP)

#     # Setup PWM channels
#     pi_pwn=GPIO.PWM(LED_accuracy,1000)
#     # It is used to start PWM generation of specified Duty Cycle.
#     pi_pwn.start(0)
#     # Setup debouncing and callbacks
#     GPIO.add_event_detect(btn_increase, GPIO.FALLING,callback=btn_increase_pressed, bouncetime=100)
#     signal.signal(signal.SIGINT, signal_handler)
#     signal.pause()

#     GPIO.add_event_detect(btn_submit, GPIO.FALLING,callback=btn_guess_pressed, bouncetime=100)
#     signal.signal(signal.SIGINT, signal_handler)
#     signal.pause()
    
#     pass