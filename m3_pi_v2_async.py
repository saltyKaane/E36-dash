#!/usr/bin/python
import obd, time, pygame, sys, os, datetime, csv, socket
from pygame.locals import *
import numpy as np
from threading import Thread

# Globals.
rpm = 0
speed = 0
coolantTemp = 0
intakeTemp = 0
MAF = 0
throttlePosition = 0
timingAdvance = 0
engineLoad = 0
dtc = None
logLength = 0
logIter = 1
connection = None
tach_iter = 0
gear = 0
fps = 0
dtc_iter = 0
priority_count = 0
ecuReady = False
startTime = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
time_elapsed_since_last_action = 0
gui_test_time = 0
debugFlag = False
piTFT = False
settingsFlag = False
ipAddr = 0
RESOLUTION = (480, 320)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
speedArr = np.array(
    [[4, 7, 10, 14, 17], [5, 9, 14, 18, 23], [7, 11, 17, 23, 28], [8, 14, 21, 28, 34], [9, 16, 24, 32, 40],
     [11, 18, 27, 37, 46], [12, 21, 31, 41, 51], [14, 23, 34, 46, 57], [15, 25, 38, 50, 63], [16, 27, 41, 55, 68],
     [18, 30, 45, 60, 74], [19, 32, 48, 64, 80], [20, 34, 51, 69, 85], [22, 37, 55, 73, 91], [23, 39, 58, 78, 97],
     [24, 41, 62, 83, 102], [26, 43, 65, 87, 108], [27, 46, 69, 92, 114], [28, 48, 72, 96, 120], [30, 50, 75, 101, 125],
     [31, 53, 79, 106, 131], [33, 55, 82, 110, 137], [34, 57, 86, 115, 142], [35, 59, 89, 119, 148],
     [37, 62, 93, 124, 154], [38, 64, 96, 129, 159]])
rpmList = np.array(
    [750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500, 4750, 5000, 5250,
     5500, 5750, 6000, 6250, 6500, 6750, 7000])


class ecuThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        global ecuReady
        global connection

        ports = obd.scan_serial()
        print(ports)

        # DEBUG: Set debug logging so we can see everything that is happening.
        obd.logger.setLevel(obd.logging.DEBUG)

        # Connect to the ECU.
        if piTFT:
            connection = obd.Async("/dev/ttyUSB0", 115200, "3", fast=False)
        else:
            connection = obd.Async("/dev/tty.usbserial-113010839615", 115200, "3", fast=False)

        # Watch everything we care about.
        connection.watch(obd.commands.RPM, callback=self.new_rpm)
        connection.watch(obd.commands.SPEED, callback=self.new_speed)
        connection.watch(obd.commands.COOLANT_TEMP, callback=self.new_coolant_temp)
        connection.watch(obd.commands.INTAKE_TEMP, callback=self.new_intake_temp)
        connection.watch(obd.commands.MAF, callback=self.new_MAF)
        connection.watch(obd.commands.THROTTLE_POS, callback=self.new_throttle_position)
        # connection.watch(obd.commands.TIMING_ADVANCE, callback=self.new_timing_advance)
        connection.watch(obd.commands.ENGINE_LOAD, callback=self.new_engine_load)
        connection.watch(obd.commands.GET_DTC, callback=self.new_dtc)

        # Start the connection.
        connection.start()

        # Set the ready flag so we can boot the GUI.
        ecuReady = True

    def new_rpm(self, r):
        global rpm
        rpm = int(r.value.magnitude)

    def new_speed(self, r):
        global speed
        speed = r.value.to("mph")
        speed = int(round(speed.magnitude))

    def new_coolant_temp(self, r):
        global coolantTemp
        coolantTemp = r.value.magnitude

    def new_intake_temp(self, r):
        global intakeTemp
        intakeTemp = r.value.magnitude

    def new_MAF(self, r):
        global MAF
        MAF = r.value.magnitude

    def new_throttle_position(self, r):
        global throttlePosition
        throttlePosition = int(round(r.value.magnitude))

    def new_timing_advance(self, r):
        global timingAdvance
        timingAdvance = int(round(r.value.magnitude))

    def new_engine_load(self, r):
        global engineLoad
        engineLoad = int(round(r.value.magnitude))

    def new_dtc(self, r):
        global dtc
        dtc = r.value


def getSpeedTest():
    global speed
    if (speed < 100):
        speed += 1
    else:
        speed = 0


def getRPMTest():
    global rpm
    rpm += 20


# Draw the given string at coordinate x,y
def drawText(string, x, y, font):
    if font == "readout":
        text = readoutFont.render(string, True, WHITE)
    elif font == "label":
        text = labelFont.render(string, True, WHITE)
    elif font == "fps":
        text = fpsFont.render(string, True, WHITE)
    textRect = text.get_rect()
    textRect.centerx = windowSurface.get_rect().centerx + x
    textRect.centery = windowSurface.get_rect().centery + y
    windowSurface.blit(text, textRect)


# Function to figure out what tach image we should display based on the RPM.
def getTach():
    global tach_iter
    if rpm == 0:
        tach_iter = 0
    elif (rpm >= 0) & (rpm < 200):
        tach_iter = 1
    elif (rpm >= 200) & (rpm < 400):
        tach_iter = 2
    elif (rpm >= 400) & (rpm < 600):
        tach_iter = 3
    elif (rpm >= 600) & (rpm < 800):
        tach_iter = 4
    elif (rpm >= 800) & (rpm < 1000):
        tach_iter = 5
    elif (rpm >= 1000) & (rpm < 1200):
        tach_iter = 6
    elif (rpm >= 1200) & (rpm < 1400):
        tach_iter = 7
    elif (rpm >= 1400) & (rpm < 1600):
        tach_iter = 8
    elif (rpm >= 1600) & (rpm < 1800):
        tach_iter = 9
    elif (rpm >= 1800) & (rpm < 2000):
        tach_iter = 10
    elif (rpm >= 2000) & (rpm < 2200):
        tach_iter = 11
    elif (rpm >= 2200) & (rpm < 2400):
        tach_iter = 12
    elif (rpm >= 2400) & (rpm < 2600):
        tach_iter = 13
    elif (rpm >= 2600) & (rpm < 2800):
        tach_iter = 14
    elif (rpm >= 2800) & (rpm < 3000):
        tach_iter = 15
    elif (rpm >= 3000) & (rpm < 3200):
        tach_iter = 16
    elif (rpm >= 3200) & (rpm < 3400):
        tach_iter = 17
    elif (rpm >= 3400) & (rpm < 3600):
        tach_iter = 18
    elif (rpm >= 3600) & (rpm < 3800):
        tach_iter = 19
    elif (rpm >= 3800) & (rpm < 4000):
        tach_iter = 20
    elif (rpm >= 4000) & (rpm < 4200):
        tach_iter = 21
    elif (rpm >= 4200) & (rpm < 4400):
        tach_iter = 22
    elif (rpm >= 4400) & (rpm < 4600):
        tach_iter = 23
    elif (rpm >= 4600) & (rpm < 4800):
        tach_iter = 24
    elif (rpm >= 4800) & (rpm < 5000):
        tach_iter = 25
    elif (rpm >= 5000) & (rpm < 5200):
        tach_iter = 26
    elif (rpm >= 5200) & (rpm < 5400):
        tach_iter = 27
    elif (rpm >= 5400) & (rpm < 5600):
        tach_iter = 28
    elif (rpm >= 5600) & (rpm < 5800):
        tach_iter = 29
    elif (rpm >= 5800) & (rpm < 6000):
        tach_iter = 30
    elif (rpm >= 6000) & (rpm < 6200):
        tach_iter = 31
    elif (rpm >= 6200) & (rpm < 6400):
        tach_iter = 32
    elif (rpm >= 6400) & (rpm < 6600):
        tach_iter = 33
    elif (rpm >= 6600) & (rpm < 6800):
        tach_iter = 34
    elif (rpm >= 6800) & (rpm < 7000):
        tach_iter = 35
    elif (rpm >= 7000) & (rpm < 7200):
        tach_iter = 36
    elif (rpm >= 7200) & (rpm < 7400):
        tach_iter = 37
    elif (rpm >= 7400) & (rpm < 7600):
        tach_iter = 38
    elif (rpm >= 7600) & (rpm < 7800):
        tach_iter = 39
    elif (rpm >= 7800) & (rpm < 8000):
        tach_iter = 40
    elif (rpm >= 8000):
        tach_iter = 41


# Given an array and a value, find what array value our value is closest to and return the index of it.
def find_nearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx


# Given RPM and speed, calculate what gear we're probably in. 
def calcGear(rpm, speed):
    global gear
    # We're stopped, so we're obviously in neutral.
    if speed == 0:
        gear = 'N'

    # We're moving but the RPM is really low, so we must be in neutral.
    # M3 seems to idle at around 800 rpm
    elif (rpm < 875) & (speed > 0):
        gear = 'N'
    # We must be in gear.
    else:
        # Find the index of the closest RPM to our current RPM.
        closestRPMIndx = find_nearest(rpmList, rpm)
        # Find the index of the closest speed to our speed.
        closestSpeedIndx = find_nearest(speedArr[closestRPMIndx], speed)
        gear = str(closestSpeedIndx + 1)


# Function to create a csv with the specified header.
def createLog(header):
    # Write the header of the csv file.
    with open('logs/' + startTime + '.csv', 'wb') as f:
        w = csv.writer(f)
        w.writerow(header)


# Function to append to the current log file.
def updateLog(data):
    with open('logs/' + startTime + '.csv', 'a') as f:
        w = csv.writer(f)
        w.writerow(data)


def closeLog():
    endTime = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    os.rename('logs/' + startTime + '.csv', 'logs/' + startTime + "_" + endTime + '.csv')


def getIP():
    global ipAddr
    ip = os.popen('ifconfig wlan0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
    ipAddr = ip.read()
    # Cludgy fix for random box character at end of string
    ipAddr = ipAddr[:-1]


def readLog(logFile):
    with open(logFile, 'rb') as f:
        reader = csv.reader(f)
        logList = list(reader)
    return logList


def getLogValues(logFile):
    global logIter
    global rpm
    global speed
    global coolantTemp
    global intakeTemp
    global MAF
    global throttlePosition
    global engineLoad

    rpm = int(logFile[logIter][1])
    speed = int(logFile[logIter][2])
    coolantTemp = logFile[logIter][3]
    intakeTemp = logFile[logIter][4]
    MAF = logFile[logIter][5]
    # Cludgy fix for issue where MAF was logged as really log float, causing clipping when displayed on GUI.
    MAF = format(float(MAF), '.2f')
    throttlePosition = logFile[logIter][6]
    engineLoad = logFile[logIter][7]
    logIter += 1
    # Reset iterator.
    if logIter == logLength:
        logIter = 1


# Connect to the ECU.
if not debugFlag:
    ecuThread()

    # Give time for the ECU to connect before we start the GUI.
    while not ecuReady:
        time.sleep(.01)

# Load all of our tach images into an array so we can easily access them.
background_dir = 'tach/'
background_files = ['%i.png' % i for i in range(0, 42)]
ground = [pygame.image.load(os.path.join(background_dir, file)) for file in background_files]

# Load the M3 PI image.
img = pygame.image.load("images/m3_logo.png")
img_button = img.get_rect(topleft=(135, 220))

# set up pygame
pygame.init()

# Set up fonts
readoutFont = pygame.font.Font("font/ASL_light.ttf", 40)
labelFont = pygame.font.Font("font/ASL_light.ttf", 30)
fpsFont = pygame.font.Font("font/ASL_light.ttf", 20)

# Set up the window. If piTFT flag is set, set up the window for the screen. Else create it normally for use on normal monitor.
if piTFT:
    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.mouse.set_visible(0)
    windowSurface = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)

else:
    windowSurface = pygame.display.set_mode(RESOLUTION, 0, 32)

# Set the caption.
pygame.display.set_caption('M3 PI')

# Create a clock object so we can display FPS.
clock = pygame.time.Clock()

# Create the csv log file with the specified header.		
createLog(["TIME", "RPM", "SPEED", "COOLANT_TEMP", "INTAKE_TEMP", "MAF", "THROTTLE_POS", "ENGINE_LOAD"])

with open('logs/' + startTime + '.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)

# Get the IP address
getIP()

if debugFlag:
    # Read the log file into memory.
    list = readLog('logs/debug_log.csv')
    # Get the length of the log.
    logLength = len(list)

# run the game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            # Rename our CSV to include end time.
            closeLog()
            # Close the connection to the ECU.
            connection.close()
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            # If mouse clicked m3 logo, load settings page.
            # Cludgy fix since resistive screen is crap
            # if img_button.collidepoint(event.pos):
            # Toggle the settings flag.
            settingsFlag = not settingsFlag

    if not debugFlag:
        # Figure out what tach image should be.
        getTach()

        # Figure out what gear we're *theoretically* in.
        calcGear(int(float(rpm)), int(speed))

    # Clear the screen
    windowSurface.fill(BLACK)

    # Load the m3 image
    windowSurface.blit(img, (windowSurface.get_rect().centerx - 105, windowSurface.get_rect().centery + 60))

    # If the settings button has been pressed:
    if (settingsFlag):
        drawText("Settings", -160, -145, "readout")
        if piTFT:
            # Print the wlan0 IP. ONLY WORKS ON LINUX
            drawText(str(ipAddr), 20, -145, "label")
        # Else print a fake ip
        else:
            drawText("192.168.1.174", 20, -145, "label")
        # Print all the DTCs
        for code, desc in dtc:
            drawText(code, 0, -80 + (dtc_iter * 50), "label")
            dtc_iter += 1
            if dtc_iter == len(dtc):
                dtc_iter = 0
        # No DTCs found.
        if not dtc:
            drawText("No DTCs found", 0, -80, "label")

    else:
        # Calculate coordinates so tachometer is in middle of screen.
        coords = (windowSurface.get_rect().centerx - 200, windowSurface.get_rect().centery - 200)

        # Load the tach image
        windowSurface.blit(ground[tach_iter], coords)

        # Draw the RPM readout and label.
        drawText(str(rpm), 0, 0, "readout")
        drawText("RPM", 0, 50, "label")

        # Draw the intake temp readout and label.
        drawText(str(intakeTemp) + "\xb0C", 190, 105, "readout")
        drawText("Intake", 190, 140, "label")

        # Draw the coolant temp readout and label.
        drawText(str(coolantTemp) + "\xb0C", -160, 105, "readout")
        drawText("Coolant", -170, 140, "label")

        # Draw the timing advance readout and label.
        # drawText(str(timingAdvance) + "\xb0", 0, 105, "readout")
        # drawText("Timing Advance", 0, 140, "label")

        # Draw the gear readout and label.
        drawText(str(gear), -190, 0, "readout")
        drawText("Gear", -190, 50, "label")

        # Draw the speed readout and label.
        drawText(str(speed) + " mph", 170, 0, "readout")
        drawText("Speed", 180, 50, "label")

        # Draw the throttle position readout and label.
        drawText(str(throttlePosition) + " %", 190, -145, "readout")
        drawText("Throttle", 190, -110, "label")

        # Draw the MAF readout and label.
        drawText(str(MAF) + " g/s", -150, -145, "readout")
        drawText("MAF", -190, -110, "label")

        # Draw the engine load readout and label.
        drawText(str(engineLoad) + " %", 0, -145, "readout")
        drawText("Load", 0, -110, "label")

        # If debug flag is set, feed fake data so we can test the GUI.
        if debugFlag:
            # Debug gui display refresh 10 times a second.
            if gui_test_time > 500:
                getLogValues(list)
                calcGear(rpm, speed)
                getTach()
                gui_test_time = 0

    # Get the current FPS and draw it.
    dt = clock.tick()
    fps = clock.get_fps()
    drawText("FPS: " + str(int(fps)), 0, 80, "fps")

    time_elapsed_since_last_action += dt
    gui_test_time += dt
    # We only want to log once a second.
    if time_elapsed_since_last_action > 1000:
        # Log all of our data.
        data = [datetime.datetime.today().strftime('%Y%m%d%H%M%S'), rpm, speed, coolantTemp, intakeTemp, MAF,
                throttlePosition, engineLoad]
        updateLog(data)

        time_elapsed_since_last_action = 0

    # draw the window onto the screen
    pygame.display.update()

    # Wait for a miniscule amount of time to give time for ECU thread to get data.
    time.sleep(.01)
