# interrupt-based GPIO example using LEDs and pushbuttons

import RPi.GPIO as GPIO
import time
import threading
import logging, logging.handlers
import board


logger = logging.getLogger('MotionSensor')

class MotionSensor:


    PIR_PIN = 17 # 11 # G17
    MICROWAVE_PIN = 27 # 13 # G27
    
    def __init__(self, motion):
        self.motion = motion

        # for GPIO numbering, choose BCM  
        GPIO.setmode(GPIO.BCM) 

        GPIO.setwarnings(True)
        GPIO.setup([MotionSensor.PIR_PIN,MotionSensor.MICROWAVE_PIN], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(MotionSensor.PIR_PIN, GPIO.BOTH, self.handle)
        GPIO.add_event_detect(MotionSensor.MICROWAVE_PIN, GPIO.BOTH, self.handle)

    def getPirState(self):
        return GPIO.input(MotionSensor.PIR_PIN)

    def getMicrowaveState(self):
        return GPIO.input(MotionSensor.MICROWAVE_PIN)

    def shutdown(self):
        logger.info("Shutdown called on motion sensor -- TODO")

    def handle(self, pin):
        # light corresponding LED when pushbutton of same color is pressed
        #GPIO.output(btn2led[pin], not GPIO.input(pin))

        pirSensorState = GPIO.input(MotionSensor.PIR_PIN)
        microwaveSensorState = GPIO.input(MotionSensor.MICROWAVE_PIN)

        if GPIO.input(pin):
            logger.info("Rising edge detected: %d PIR:%d MW:%d",pin,pirSensorState,microwaveSensorState)
        else:
            logger.info("Falling edge detected: %d PIR:%d MW:%d",pin,pirSensorState,microwaveSensorState)

        if pirSensorState and microwaveSensorState:
            logger.info("BOTH triggered!!") 
        elif pirSensorState:
            logger.info("PIR Motion") 
        elif microwaveSensorState:
            logger.info("Microwave Motion") 
        else:
            logger.info("No Motion") 


