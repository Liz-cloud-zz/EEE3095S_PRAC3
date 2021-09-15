# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
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

# initialse global variables
eeprom = ES2EEPROMUtils.ES2EEPROM()
pi_pwnL=None
pi_pwnB=None
curr_guess=0
username=None
trials=0
value=0


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
    print("curr_guess the number and immortalise yourascii_val in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    global value
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        setup()
        time.sleep(0.5)
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your curr_guess!")
        print("Press and hold the curr_guess button to cancel your game")
        value = generate_number()
        # print("value to be gueesed=",value)
        while not end_of_game:
            pass
        welcome()
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    raw_data.sort(key=lambda x: x[1]) # sort the scores
    if count>2:
        for i in range(1,4):
            data=raw_data[i-1]
            print("{} -{} took {} guesses".format(i,data[0],data[1]))
    else:
        for i in range(1,count+1):
            data=raw_data[i-1]
            print("{} -{} took {} guesses".format(i,data[0],data[1]))
    pass

# Setup Pins
def setup():
    # declare global variables for buzzer and LED PWN
    global pi_pwnB
    global pi_pwnL

    GPIO.setwarnings(False)

    # Setup board mode
    GPIO.setmode(GPIO.BOARD)

    try:
        # Setup regular GPIO:
        # Set LEDS for outputs 
        # turn off LEDS
        GPIO.setup(LED_value, GPIO.OUT) 
        GPIO.output(LED_value,GPIO.LOW)

        # Set buttons for input
     
        GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)

        # Setup PWM channels
        # for LED
        # print("set led2 pwn")
        GPIO.setup(LED_accuracy,GPIO.OUT)
        pi_pwnL=GPIO.PWM(LED_accuracy,1000)
        pi_pwnL.start(0) # start() is used to start PWM generation of specified Duty Cycle.
        # for Buzzer
        GPIO.setup(buzzer,GPIO.OUT)
        pi_pwnB=GPIO.PWM(buzzer,1000)
        pi_pwnB.start(0)   # start() is used to start PWM generation of specified Duty Cycle.
       
        # start() is used to start PWM generation of specified Duty Cycle.
        pi_pwnB.start(0)
        time.sleep(0.5) # delay

        # Setup debouncing and callbacks
        GPIO.add_event_detect(btn_increase, GPIO.FALLING,callback=btn_increase_pressed, bouncetime=500)
        GPIO.add_event_detect(btn_submit, GPIO.FALLING,callback=btn_curr_guess_pressed, bouncetime=500)

    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        print("Keyboard interrupt")
   
    pass

# convert to ASCII val
def converttoASC(val):
    ascii_val=''
    for i in val:
       ascii_val=ascii_val + chr(i)
    return ascii_val

# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores
    score_count=eeprom.read_byte(0x00)
    time.sleep(0.5)
    initial_scores=eeprom.read_block(1,score_count*4) # get data from eeprom
    # convert the codes back to ascii
    scores=[]
    for i in range(0,len(initial_scores),4):
        scores.append([converttoASC(initial_scores[i:i+3]),initial_scores[i+3]])
    # return back the results
    return score_count, scores


# Save high scores
def save_scores(updated_score):
    # fetch scores
    initial_score_count, initial_scores=fetch_scores()
    # include new score
    initial_scores.append(updated_score)
    # sort
    initial_scores.sort(key=lambda x: x[1])
    output_scores=[]
    #covert data from acii to binary for storage in the eeprom
    for score in initial_scores:
        for chart in score[0]:
            output_scores.append(ord(chart))
        output_scores.append(score[1])

    # update total amount of scores
    eeprom.clear((initial_score_count+1)*4)
    time.sleep(0.1)
    eeprom.write_block(0x00,[initial_score_count+1])
    time.sleep(0.1)

    # write new scores
    eeprom.write_block(1,output_scores)
    print("score saved to eeprom!")

    pass


# Generate curr_guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)

# Increase button pressed
def btn_increase_pressed(channel):
    # You can choose to have a global variable store the user's current curr_guess, 
    # or just pull the value off the LEDs when a user makes a curr_guess
    # define global variable for guess
    global curr_guess
    # print("guess pressed!")
    # Increase the value shown on the LEDs
    if curr_guess==1:# LED1=ON, LED2=OFF, LED3=OFF
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.LOW)
    elif curr_guess==2:# LED1=OFF, LED2=ON, LED3=OFF
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.LOW)
    elif curr_guess==3:# LED1=ON, LED2=ON, LED3=OFF
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.LOW)
    elif curr_guess==4:# LED1=OFF, LED2=OFF, LED3=ON
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.HIGH)
    elif curr_guess==5:# LED1=ON, LED2=OFF, LED3=ON
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.HIGH)
    elif curr_guess==6:# LED1=OFF, LED2=ON, LED3=ON
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.HIGH)
    elif curr_guess==7:# LED1=ON, LED2=ON, LED3=ON
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.HIGH)
    else:
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.LOW)
    # print("guess value =",curr_guess)
    if(curr_guess==7):# reset guess
        curr_guess=0
    else: 
        curr_guess+=1# increment curr_guess number
    pass


# curr_guess button
def btn_curr_guess_pressed(channel):
    # declare global variables
    global trials
    global curr_guess
    global value
    global username
    global eeprom
    # print("guess submitted!")
    start=time.time()# get start time when button is pressed
    # If they've pressed and held the button,
    while GPIO.input(channel)==0:
        pass

    button_time=time.time()-start # get the difference when button is pressed and realsed

    if ( .1 <=button_time < 2): # if less than 2 seconds , increment number of guess trials
        trials+=1
        # print("number of trials is : ",trials)
        # adjust the current guess value
        if curr_guess==0:
            curr_guess=7
        else:
            curr_guess-=1

        # Compare the actual value with the user value displayed on the LEDs
        if (value==curr_guess):  # if it's an exact curr_guess:
            print("correct guess value! ")
         
            # - Disable LEDs and Buzzer
            GPIO.output(LED_value,GPIO.LOW)
            accuracy_leds()
            trigger_buzzer()
            
            # - tell the user and prompt them for aascii_val
            username=input("Enter your name: ")

            # - fetch all the scores
            # - add the new score
            # - sort the scores
            # - Store the scores back to the EEPROM, 
            # being sure to update the score count
            save_scores([username[:3],trials])
            end_of_game=False

            # clear up the GPIO and take them back to the menu screen
            GPIO.cleanup()
            time.sleep(0.5)
            menu()
            pass
        else:
            # print("all guess leds lit up")
            GPIO.output(LED_value,GPIO.HIGH)
            # Change the PWM LED
            accuracy_leds()
            # if it's close enough, adjust the buzzer
            trigger_buzzer()
            curr_guess=0# reset guesses

            # clear up the GPIO and take them back to the menu screen
            GPIO.cleanup()
            time.sleep(0.5)
            menu()

    elif (2 <= button_time):
        end_of_game=False
         # - Disable LEDs and Buzzer
        curr_guess=value
        accuracy_leds()
        trigger_buzzer()
        # end the game
        GPIO.cleanup()
        time.sleep(0.5)
        menu()
    pass


# LED Brightness
def accuracy_leds():
    global pi_pwnL
    global curr_guess
    global value
    # Set the brightness of the LED based on how close the curr_guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user curr_guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they curr_guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
#    try:
    duty=0
    if(curr_guess>value):
        duty=((8-curr_guess)/(8-value))*100
        pi_pwnL.ChangeDutyCycle(duty)
        if(duty==0):
                 pi_pwnL.stop()
    elif(value==0 and curr_guess!= value):
        duty=(curr_guess/8)*100
        pi_pwnL.ChangeDutyCycle(duty)
        if(duty==0):
                 pi_pwnL.stop()
    elif(curr_guess<value):
            duty=((8-value)/(8-curr_guess))*100
            pi_pwnL.ChangeDutyCycle(duty)
            if(duty==0):
                 pi_pwnL.stop()

    elif(curr_guess==value):
        duty=0
        pi_pwnL.ChangeDutyCycle(duty)
        pi_pwnL.stop()
 

#    except KeyboardInterrupt:
#        print("interrupt occured!")
    pass
    

# Sound Buzzer
def trigger_buzzer():
    global pi_pwnB
    global curr_guess
    global value
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
   
    diff=abs(value-curr_guess)
    # print("current guess",curr_guess)
    # print("guess val",value)
    # print("difference is=",diff)
    # try:
    if(diff==3):  # If the user is off by an absolute value of 3, the buzzer should sound once every second
        pi_pwnB.ChangeFrequency(1)
    elif(diff==2):  # If the user is off by an absolute value of 2, the buzzer should sound twice every second
        pi_pwnB.ChangeFrequency(2)
    elif(diff==1):  # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
        pi_pwnB.ChangeFrequency(4)# 4 sec
    elif(diff==0):# stop buzzer
        pi_pwnB.stop()
    else:# start buzzer
        time.sleep(0.5)
        pi_pwnB.start(50)
    time.sleep(0.5)
  
    # except KeyboardInterrupt:
    #     print("interrupt occured!")
    pass

if __name__ == "__main__":
    try:
        # Call welcome function
        welcome()
        while True:
            # Call menu function
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
