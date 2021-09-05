import RPi.GPIO as GPIO

def setUp():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.IN)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(GPIO.input(23))
    print(not GPIO.input(23))
    GPIO.setup([12,13,17,27,22], GPIO.OUT)
    while not GPIO.input(23) == GPIO.LOW:
        GPIO.output([12, 13,17,27,22], GPIO.HIGH)

    print("button was pressed")

    GPIO.cleanup()