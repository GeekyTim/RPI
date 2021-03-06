#coding=utf-8

import RPi.GPIO as GPIO
import struct
import smbus
import sys
import time
import os

Sensor_ADDRESS		= 0x48

#Set global alert temperature;
ALERT_CON_TEMPERATURE   = 36

#Set global CPU temperature
ALERT_CPU_TEMPERATURE   = 70

TEMP_REGISTER 	    = 0
CONF_REGISTER 	    = 1
#THYST_REGISTER 	  = 2
#TOS_REGISTER 	    = 3

#CONF_SHUTDOWN       = 0
#CONF_OS_COMP_INT    = 1
#CONF_OS_POL 	    = 2
#CONF_OS_F_QUE 	    = 3

GPIO_PIN = 12
g_on = False

def regdata2float (regdata):
	return (regdata / 32.0) / 8.0

def toFah(temp):
	return (temp * (9.0/5.0)) + 32.0

def setAlertTemp():
	g_bus.write_byte_data(Sensor_ADDRESS,TEMP_REGISTER,ALERT_CON_TEMPERATURE)

def clearAlert():
	g_bus.write_byte_data(Sensor_ADDRESS,CONF_REGISTER,0x00)

#Initialize the sensor and others.
def init():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(GPIO_PIN, GPIO.OUT)
	GPIO.setwarnings(False)
	setAlertTemp()
	clearAlert()

def getTemp(self):
	#msg = "Reads the temp from the sensor";
	raw = g_bus.read_word_data(Sensor_ADDRESS, TEMP_REGISTER) & 0xFFFF
	raw = ((raw << 8) & 0xFF00) + (raw >> 8)
	ret = regdata2float(raw)
	print "Current condition temperature is ", ret, "℃", "[", ALERT_CON_TEMPERATURE,"℃]"
	return ret

def getCPUtemp():
	cTemp = os.popen('vcgencmd measure_temp').readline()
	ret = float(cTemp.replace("temp=","").replace("'C\n",""))
	print "Current CPU temperature is ", ret, "℃", "[", ALERT_CPU_TEMPERATURE,"℃]"
	return ret

def checkTemperature():
	return (getTemp(g_bus) > ALERT_CON_TEMPERATURE) or (getCPUtemp() > ALERT_CPU_TEMPERATURE)

def setFan(need_to_open):
	#turn on the fan
	global g_on
	if (g_on and need_to_open) :
		return

	if (g_on == False and need_to_open == False) :
		return

	if need_to_open :
		if g_on == False :
			print "starup fan!"
		GPIO.output(GPIO_PIN,GPIO.LOW)
		g_on = True
	else:
		if g_on :
			print "Stop fan!"
		GPIO.output(GPIO_PIN,GPIO.HIGH)
		g_on = False

g_bus = smbus.SMBus(1)
init()
while True:
	print "------------------"
	print time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime())
	setFan(checkTemperature())
	time.sleep(3);