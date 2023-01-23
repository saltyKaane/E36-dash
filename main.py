import obd
import time
import pygame
import sys, os, datetime, csv, socket, math
import threading

connection = None
ecuReady = False
connectionEnabled = False

class ecuThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        global ecuReady
        global connection
        global connectionEnabled

        ports = obd.scan_serial()
        print(ports)

        # DEBUG: Set debug logging so we can see everything that is happening.
        obd.logger.setLevel(obd.logging.DEBUG)
        connection = obd.Async(fast=False)

        # Watch everything we care about.
        connection.watch(obd.commands.RPM, callback=self.new_rpm)

        # Start the connection.
        connection.start()

        # Set the ready flag so we can boot the GUI.
        ecuReady = True

        connectionEnabled = True


    def new_rpm(self, r):
        global rpm
        rpm = int(r.value.magnitude)

ecuThread()
while not ecuReady:
    time.sleep(.01)



print('hello world')
