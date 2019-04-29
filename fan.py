#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import sys
import sqlite3

# Configuration
FAN_PIN = 21            # BCM pin used to drive transistor's base
WAIT_TIME = 10           # [s] Time to wait between each refresh
FAN_MIN = 40            # [%] Fan minimum speed.
PWM_FREQ = 25           # [Hz] Change this value if fan has strange behavior

# Configurable temperature and fan speed steps
tempSteps = [40, 50]    # [°C]
speedSteps = [50, 100]   # [%]

# Fan speed will change only of the difference of temperature is higher than hysteresis
hyst = 1

# Setup GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)
fan=GPIO.PWM(FAN_PIN,PWM_FREQ)
fan.start(0);

i = 0
cpuTempOld=0
fanSpeedOld=0
fanSpeed = 0

conn = sqlite3.connect('cpu_temp.db')
db = conn.cursor()
db.execute('''
        create table if not exists cpu_temp
        (id integer primary key autoincrement,
        datetime real,
        cpu_temp integer,
        fan_speed integer
        )
        ''')

# We must set a speed value for each temperature step
if(len(speedSteps) != len(tempSteps)):
    print("Numbers of temp steps and speed steps are different")
    exit(0)
try:
    while (1):
        # Read CPU temperature
        cpuTempFile=open("/sys/class/thermal/thermal_zone0/temp","r")
        cpuTemp=int(cpuTempFile.read())/1000
        cpuTempFile.close()
        if(cpuTemp >= tempSteps[1]):
            fanSpeed = speedSteps[1]
        if(cpuTemp < tempSteps[0]):
            fanSpeed = 0
        if(fanSpeed != 0):
            fanSpeed = round((speedSteps[1]-speedSteps[0])\
                       /(tempSteps[1]-tempSteps[0])\
                       *(cpuTemp-tempSteps[0])\
                       +speedSteps[0],1)
        
        print "CPU:", cpuTemp, "°C, fan running at ", fanSpeed
        db.execute('''insert into cpu_temp(datetime, cpu_temp, fan_speed)values(julianday('now'),?,?)''', (cpuTemp, fanSpeed))
        conn.commit()
        if((fanSpeed != fanSpeedOld) ):
            if((fanSpeed >= FAN_MIN) or (fanSpeed == 0)):
                fan.ChangeDutyCycle(fanSpeed)
                fanSpeedOld = fanSpeed                

        # Wait until next refresh
        time.sleep(WAIT_TIME)

# If a keyboard interrupt occurs (ctrl + c), the GPIO is set to 0 and the program exits.
except(KeyboardInterrupt):
    print("Fan ctrl interrupted by keyboard")
    conn.close()
    GPIO.cleanup()
    sys.exit()
