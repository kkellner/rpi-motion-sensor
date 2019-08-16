#!/usr/bin/python3
# Motion Sensor publish to MQTT
# 
# xxxxxxxxxxxxxx

import RPi.GPIO as GPIO
import time
import threading
import time
import board
import logging, logging.handlers 
import signal
import sys
import os

from http_request import HttpServer
from rpi_info import RpiInfo
from motion_sensor import MotionSensor


logger = logging.getLogger('motion')


class Motion:
    """Handle Motion monitor / publish events """

    def __init__(self):
        self.server = None
        self.rpi_info = None
        self.motion_sensor = None

        # Docs: https://docs.python.org/3/library/logging.html
        # Docs on config: https://docs.python.org/3/library/logging.config.html
        FORMAT = '%(asctime)-15s %(threadName)-10s %(levelname)6s %(message)s'
        logging.basicConfig(level=logging.NOTSET, format=FORMAT)
  
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        GPIO.setwarnings(True)

    def __setup_logger(self, logger_name, log_file, level=logging.INFO):
        l = logging.getLogger(logger_name)
        FORMAT = '%(asctime)-15s %(message)s'
        formatter = logging.Formatter(FORMAT)
        # Docs: https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler
        fileHandler = logging.handlers.RotatingFileHandler(log_file, mode='a',
                                                           maxBytes=1000000, backupCount=2)
        fileHandler.setFormatter(formatter)
        l.setLevel(level)
        l.addHandler(fileHandler)
        l.propagate = False
  
    def signal_handler(self, signal, frame):
        logger.info('Shutdown...')
        if self.server is not None:
            self.server.shutdown()
        if self.motion_sensor is not None:
            self.motion_sensor.shutdown()
        GPIO.cleanup()
        sys.tracebacklimit = 0
        sys.exit(0)

    def startup(self):
        logger.info('Startup...')
        self.rpi_info = RpiInfo(self)
        self.motion_sensor = MotionSensor(self)

        self.server = HttpServer(self)
        # the following is a blocking call
        self.server.run()


def main():
    """
    The main function
    :return:
    """
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

    motion = Motion()
    motion.startup()


if __name__ == '__main__':
    main()
