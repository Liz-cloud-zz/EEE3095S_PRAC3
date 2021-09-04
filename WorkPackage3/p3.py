# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import signal
import sys

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = None
eeprom = ES2EEPROMUtils.ES2EEPROM()
pi_pwn=0


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    pass

#use the signal module to be able to handle and make the program pause indefinitely.
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)

    # Setup regular GPIO:
    # Set LEDS for outputs 
    for i in range (len(LED_value)):
        GPIO.setup(LED_value[i], GPIO.OUTPUT) # set GPIO pins as input  
    GPIO.set(LED_accuracy,GPIO.OUTPUT)
    # Set buttons for input
    GPIO.setup(btn_increase,GPIO.IN,pull_up=GPIO.PUD_UP)
    GPIO.setup(btn_submit,GPIO.IN,pull_up=GPIO.PUD_UP)

    # Setup PWM channels
    pi_pwn=GPIO.PWM(LED_accuracy,1000)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.FALLING,callback=btn_increase_pressed, bouncetime=100)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

    GPIO.add_event_detect(btn_submit, GPIO.FALLING,callback=btn_guess_pressed, bouncetime=100)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
    
    pass

# convert to ASCII val
def convertASC(val=None):
    return ''.join([chr(int(x, 2)) for x in val])

# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores
    scores=eeprom.read_block(0,3)
    # convert the codes back to ascii
    for i in range (len(scores)):
        for x in range (len(scores[i])):
            scores[i][x]=converttoASC(scores[i][x])
            score_count+=1
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    score_count, scores=fetch_scores()
    # include new score

    # sort
    scores.sort(key=lambda x: x[1])
    # update total amount of scores

    # write new scores
    eeprom.write_block(0,scores)
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)
# LED blink method
def blinker(should_blink,LED_GPIO)
     while True:
        if should_blink:
            GPIO.output(LED_GPIO, GPIO.HIGH) 
        time.sleep(0.5)
        if should_blink:
            GPIO.output(LED_GPIO, GPIO.LOW)  
        time.sleep(0.5)
    
# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    global guess=0
    global should_blink=False
    
    # or just pull the value off the LEDs when a user makes a guess
    if not GPIO.input(btn_increase):
        guess+=1# increment guess number
        if (guess==0): # LED1=OFF, LED2=OFF, LED3=OFF
            GPIO.output(LED_value[0],GPIO.LOW)

        elif(guess==1):# LED1=BLINK, LED2=OFF, LED3=OFF
            should_blink=not should_blink
            blinker(should_blink,LED_value[0])

        elif(guess==2):# LED1=ON, LED2=OFF, LED3=OFF
            GPIO.output(LED_value[0],GPIO.HIGH)

        elif (guess==3):# LED1=BLINK, LED2=BLINK, LED3=OFF
            should_blink=not should_blink
            blinker(should_blink,LED_value[0])
            
            should_blink=not should_blink
            blinker(should_blink,LED_value[1])

        elif(guess==4):# LED1=ON, LED2=BLINK, LED3=OFF
            GPIO.output(LED_value[0],GPIO.HIGH)
            should_blink=not should_blink
            blinker(should_blink,LED_value[1])

        elif(guess==5):# LED1=ON, LED2=ON, LED3=OFF
            GPIO.output(LED_value[0],GPIO.HIGH)
            GPIO.output(LED_value[1],GPIO.HIGH)

        elif (guess==6):# LED1=BLINK, LED2=BLINK, LED3=BLINK
            should_blink=not should_blink
            blinker(should_blink,LED_value[0])
            
            should_blink=not should_blink
            blinker(should_blink,LED_value[1])
            
            should_blink=not should_blink
            blinker(should_blink,LED_value[2])

        elif(guess==7):# LED1=HIGH, LED2=ON, LED3=BLINK
            GPIO.output(LED_value[0],GPIO.HIGH)
            GPIO.output(LED_value[1],GPIO.HIGH)

            should_blink=not should_blink
            blinker(should_blink,LED_value[2])

        elif(guess==8):# LED1=ON, LED2=ON, LED3=ON
            GPIO.output(LED_value[0],GPIO.HIGH)
            GPIO.output(LED_value[1],GPIO.HIGH)
            GPIO.output(LED_value[2],GPIO.HIGH)
    else:
        print("button increase released!")
        GPIO.output(LED_value[i],GPIO.LOW)
     pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
      if not GPIO.input(btn_submit):
         print("Button submit pressed!")
         GPIO.cleanup()
         menu()
         # Compare the actual value with the user value displayed on the LEDs
         # Change the PWM LED
         # if it's close enough, adjust the buzzer
         if (value==guess):  # if it's an exact guess:
             for i in range (len(LED_value)): # - Disable LEDs and Buzzer
                 GPIO.output(LED_value[i], LOW)
             # - tell the user and prompt them for a name
             username=input()
             print("Enter your name: "+username)
             # - fetch all the scores
             score_count, scores=fetch_scores()
             # - add the new score
             # - sort the scores
             scores.sort(key=lambda x: x[1])
             # - Store the scores back to the EEPROM, 
             # being sure to update the score count
             eeprom.write_block(0,scores)
             
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
