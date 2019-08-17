# interrupt-based GPIO example using LEDs and pushbuttons

import RPi.GPIO as GPIO
import time
import threading
import logging, logging.handlers
import board
import paho.mqtt.client as mqtt
import json

logger = logging.getLogger('MotionSensor')

class MotionSensor:


    PIR_PIN = 17 # 11 # G17
    MICROWAVE_PIN = 27 # 13 # G27
    
    mqttBrokerHost = "rpicontroller1.hyperboard.net"
    mqttBrokerPort = 1883
    sensorQueueName = "yukon/driveway/motionSensorA"

    queueNamespace = "yukon"
    nodeName = "drivewayMotionSensorA"
    deviceName = "deviceA"
    queueNodeStatus = queueNamespace + "/node/" + nodeName + "/status"
    queueDeviceStatus = queueNamespace + "/device/" + nodeName + "/" + deviceName + "/status"


    def __init__(self, motion):
        self.motion = motion

        # for GPIO numbering, choose BCM  
        GPIO.setmode(GPIO.BCM) 

        GPIO.setwarnings(True)
        GPIO.setup([MotionSensor.PIR_PIN,MotionSensor.MICROWAVE_PIN], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Connect to MQTT broker
        self.client = mqtt.Client(client_id=MotionSensor.nodeName)
        mqttLogger = logging.getLogger('mqtt')
        self.client.enable_logger(mqttLogger)
        self.client.reconnect_delay_set(1, 30)
        self.client.max_queued_messages_set(10)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        deathPayload = "DISCONNECTED"
        self.client.will_set(MotionSensor.queueNodeStatus, deathPayload, 0, True)

        self.client.connect_async(MotionSensor.mqttBrokerHost,MotionSensor.mqttBrokerPort,60)

        self.client.loop_start()

        GPIO.add_event_detect(MotionSensor.PIR_PIN, GPIO.BOTH, self.handle)
        GPIO.add_event_detect(MotionSensor.MICROWAVE_PIN, GPIO.BOTH, self.handle)


    ######################################################################
    # Publish the BIRTH certificates
    ######################################################################
    def publishBirth(self):
        self.publishNodeBirth()
        self.publishDeviceBirth()

    ######################################################################
    # Publish the NBIRTH certificate
    ######################################################################
    def publishNodeBirth(self):
        logger.info("Publishing Node Birth")
        payload = "ONLINE"
        self.client.publish(MotionSensor.queueNodeStatus, payload, 0, True)

    ######################################################################
    # Publish the DBIRTH certificate
    ######################################################################
    def publishDeviceBirth(self):
        logger.info("Publishing Device Birth")
        payload = "TBD"
        self.client.publish(MotionSensor.queueDeviceStatus, payload, 0, True)

    ######################################################################
    # Publish the NBIRTH certificate
    ######################################################################
    def publishNodeOffline(self):
        logger.info("Publishing Node Birth")
        payload = "OFFLINE"
        self.client.publish(MotionSensor.queueNodeStatus, payload, 0, True)
        
    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code "+str(rc))
        self.publishBirth()

    def on_disconnect(self, client, userdata, rc):
        logger.warn("Disconnected with result code "+str(rc))

    def getPirState(self):
        return GPIO.input(MotionSensor.PIR_PIN)

    def getMicrowaveState(self):
        return GPIO.input(MotionSensor.MICROWAVE_PIN)

    def shutdown(self):
        logger.info("Shutdown -- disconnect from MQTT broker")
        self.publishNodeOffline()
        self.client.loop_stop()
        self.client.disconnect()
        #GPIO.cleanup()


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

        data = {
            "eventPin": pin,
            "motionPirState" : pirSensorState,
            "motionMicrowaveState": microwaveSensorState,
            "time" : time.time(),
            "otherdata" : "some data"
        }
        self.publishEventObject(MotionSensor.sensorQueueName, data)


    def publishEventObject(self, eventQueue, eventData):
        data_out=json.dumps(eventData) # encode object to JSON
        return self.publishEventString(eventQueue, data_out)

    def publishEventString(self, eventQueue, eventString):
        logger.info("Publish to queue [%s] data: [%s]", eventQueue, eventString)
        msg_info = self.client.publish(eventQueue, eventString, qos=0)
        #msg_info.wait_for_publish()
        return msg_info


