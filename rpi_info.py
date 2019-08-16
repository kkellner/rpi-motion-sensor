

import subprocess
import logging
import time

logger = logging.getLogger('display')


class RpiInfo:

    def __init__(self, fountain):
        self.dataMap = {}
        self.lastUpdate = None

    def get_info(self):
        now = time.time()
        if self.lastUpdate is None or now > self.lastUpdate + 1:
            # Only update every n seconds
            self.lastUpdate = now
            self.update()

        return self.dataMap

    def update(self):
        localDataMap = {}
        self.runColonOutputCommand(localDataMap, "iw wlan0 link")
        self.runColonOutputCommand(localDataMap, "iw wlan0 station dump")
        self.runColonOutputCommand(localDataMap, "iw dev wlan0 link")
        #logger.info("dataMap: " + str(localDataMap))
        self.dataMap = localDataMap

    def runColonOutputCommand(self, dataMap, cmd):

        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        cmdOutput = p.stdout.strip()

        lines = cmdOutput.splitlines()
        for line in lines:
            keyValue = line.split(':')
            if len(keyValue) == 2:
                dataMap[keyValue[0].strip()] = keyValue[1].strip()

        return dataMap
        
