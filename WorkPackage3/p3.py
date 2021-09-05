# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import signal
import sys
import time
import math
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
global pi_pwnL,pi_pwnB
pi_pwnL=None
pi_pwnB=None
global curr_guess
curr_guess=0
global username
username=None


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
    print("curr_guess the number and immortalise your name in the High Score Hall of Fame!")


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
        print("Use the buttons on the Pi to make and submit your curr_guess!")
        print("Press and hold the curr_guess button to cancel your game")
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
# def signal_handler(sig, frame):
#     GPIO.cleanup()
#     sys.exit(0)

# Setup Pins
def setup():
    GPIO.setwarnings(False)
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    print("setmode is Board")

    try:
        # Setup regular GPIO:
        # Set LEDS for outputs 
        for i in range (len(LED_value)):
            GPIO.setup(LED_value[i], GPIO.OUT) # set GPIO pins as input  
        GPIO.setup(LED_accuracy,GPIO.OUT)
        # Set buttons for input
        GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        #Set buzzer for output
        GPIO.setup(buzzer,GPIO.OUT)

        # Setup PWM channels
        pi_pwnL=GPIO.PWM(LED_accuracy,1000)# for LED
        pi_pwnL=GPIO.PWM(buzzer,1000)# for Buzzer
        # It is used to start PWM generation of specified Duty Cycle.
        pi_pwnL.start(0)
        # Setup debouncing and callbacks
        GPIO.add_event_detect(btn_increase, GPIO.RISING,callback=btn_increase_pressed, bouncetime=100)
        GPIO.add_event_detect(btn_submit, GPIO.RISING,callback=btn_curr_guess_pressed, bouncetime=100)

    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        print("Keyboard interrupt")

    except:
        print("some error") 

    finally:
        print("clean up") 
        GPIO.cleanup() # cleanup all GPIO 
    pass

# convert to ASCII val
def converttoASC(val=None):
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
    scores.append([username,curr_guess])
    # sort
    scores.sort(key=lambda x: x[1])
    # update total amount of scores
    score_count+=1
    # write new scores
    eeprom.write_block(0,scores)
    pass


# Generate curr_guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)

# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current curr_guess, 
    # or just pull the value off the LEDs when a user makes a curr_guess
    if not GPIO.input(btn_increase):
        print("button increase pressed!")
        curr_guess+=1# increment curr_guess number
        if curr_guess==1:# LED1=ON, LED2=OFF, LED3=OFF
            LED_value[0]=GPIO.HIGH
            LED_value[1]=GPIO.LOW
            LED_value[2]=GPIO.LOW
        elif curr_guess==2:# LED1=OFF, LED2=ON, LED3=OFF
            LED_value[0]=GPIO.LOW
            LED_value[1]=GPIO.HIGH
            LED_value[2]=GPIO.LOW
        elif curr_guess==3:# LED1=ON, LED2=ON, LED3=OFF
            LED_value[0]=GPIO.HIGH
            LED_value[1]=GPIO.HIGH
            LED_value[2]=GPIO.LOW
        elif curr_guess==4:# LED1=OFF, LED2=OFF, LED3=ON
            LED_value[0]=GPIO.LOW
            LED_value[1]=GPIO.LOW
            LED_value[2]=GPIO.HIGH
        elif curr_guess==5:# LED1=ON, LED2=OFF, LED3=ON
            LED_value[0]=GPIO.HIGH
            LED_value[1]=GPIO.LOW
            LED_value[2]=GPIO.HIGH
        elif curr_guess==6:# LED1=OFF, LED2=ON, LED3=ON
            LED_value[0]=GPIO.LOW
            LED_value[1]=GPIO.HIGH
            LED_value[2]=GPIO.HIGH
        elif curr_guess==7:# LED1=ON, LED2=ON, LED3=ON
            LED_value[0]=GPIO.HIGH
            LED_value[1]=GPIO.HIGH
            LED_value[2]=GPIO.HIGH
    else:
        print("button increase released!")
        GPIO.OUT(LED_value[i],GPIO.LOW)
    pass


# curr_guess button
def btn_curr_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    if not GPIO.input(btn_submit):
        print("Button submit pressed!")
        #GPIO.cleanup()
        menu()
        # Compare the actual value with the user value displayed on the LEDs
        # Change the PWM LED
        accuracy_leds()
        # if it's close enough, adjust the buzzer
        if (value==curr_guess):  # if it's an exact curr_guess:
            # - Disable LEDs and Buzzer
            for i in range (len(LED_value)): 
                GPIO.OUT(LED_value[i], LOW)
            pi_pwnL.stop()
            pi_pwnB.stop()
            # - tell the user and prompt them for a name
            username=input()
            print("Enter your name: "+username)
            # - fetch all the scores
            # - add the new score
            # - sort the scores
            # - Store the scores back to the EEPROM, 
            # being sure to update the score count
            save_scores()
          
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the curr_guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user curr_guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they curr_guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
   try:
       duty=((8-curr_guess)/(8-value))*100
       pi_pwnL.ChangeDutyCycle(duty)
       sleep(0.01)
   except KeyboardInterrupt:
       print("interrupt occured!")
   pass
    

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    diff=abs(value-curr_guess)
    try:
        if(diff==3):
            pi_pwnB.ChangeDutyCycle(50)# 1 sec
            sleep(0.1)
        elif(diff==2):
            pi_pwnB.ChangeDutyCycle(50)#1 sec
            sleep(0.1)
            pi_pwnB.ChangeDutyCycle(50)# 2sec
            sleep(0.1)
        elif(diff==1):
            pi_pwnB.ChangeDutyCycle(50)# 1 sec
            sleep(0.1)
            pi_pwnB.ChangeDutyCycle(50)# 2 sec
            sleep(0.1)
            pi_pwnB.ChangeDutyCycle(50)# 3 sec
            sleep(0.1)
            pi_pwnB.ChangeDutyCycle(50)# 4 sec
            sleep(0.1)
    except KeyboardInterrupt:
        print("interrupt occured!")
    pass



if __name__ == "__main__":
    try:
        # Call setup function
        print("main method evocked")
        setup()
        print("set up done!")
        welcome()
        print("wlecome message displayed")
        while True:
            menu()
            print("menu displayed")
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
