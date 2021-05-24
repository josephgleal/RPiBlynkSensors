import blynklib
import random
import adafruit_dht
import board
import os
import sys
import subprocess
import time

# TODO
# error handling for when first reading fails
# test on Pi zero instead of Pi 4
# if Pi zero has issues, use a for loop inside the while loop to impliment an average, while also still utilizing the sleep function
# impliment error logging


#######################start up ######################

# This function kills the "libgpiod_pulsei" prior to initializing a blynk object.
# This is necessary to prevent an error where the GPIO cannot be set up if that process is running.
def startUp():
    try:
        process = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        output, error = process.communicate()
        # print(output)
        targetProcess = "libgpiod_pulsei"
        for line in output.splitlines():
            if targetProcess in str(line):
                pid = int(line.split(None,1)[0])
                os.kill(pid,9)
    except:
        print("nothing")
startUp()

BLYNK_AUTH = 'k23bFgoarBaCRdw7BxUTivijuj7Gatk0' #use your auth token here
blynk = blynklib.Blynk(BLYNK_AUTH)

DHT_PIN = 4
dht_device = adafruit_dht.DHT22(board.D4)
Celcius = 0
temperature = 0
humidity = 0

highHumidity = False
lowHumidity = False
lowTemperature = False
highTemperature = False

###########functions#####################
READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"
@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):
    
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, temperature)
    

@blynk.handle_event('read V1')
def read_virtual_pin_handler(pin):
    
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, humidity)

# Retrieves temperature data and optionally pushes to supergraph on pin V2
def getTemperature():
    global temperature
    try:
        Celcius = dht_device.temperature
        temperature = (Celcius * 9/5)+32
        blynk.virtual_write(2, temperature)
        return temperature
    except RuntimeError:
        print("error with temperature reading")
    except TypeError:
        print("try again")

# Retrieves humidity data and optionally pushes to supergraph on pin V3
def getHumidity():
    global humidity
    try:
        humidity = dht_device.humidity
        blynk.virtual_write(3, humidity)
        return humidity
    except RuntimeError:
        print("error with humidity reading")
        
def warnHumidity(low, high):
    lowError = "Humidity below " + str(low) + " detected"
    highError = "Humidity above " + str(high) + "% detected"
    global lowHumidity
    global highHumidity
    if humidity > high and highHumidity == False:
        blynk.notify(highError)
        highHumidity = True
    elif humidity < low and lowHumidity == False:
        blynk.notify(lowError)
        lowHumidity = True
    elif humidity < high and humidity > low:
        highHumidity = False
        lowHumidity = False
        
def warnTemperature(low, high):
    lowError = "Temperature below " + str(low) + "F detected"
    highError = "Temperature above " + str(high) + "F detected"
    global lowTemperature
    global highTemperature
    try:
        if temperature > high and highTemperature == False:
            blynk.notify(highError)
            highTemperature = True
        elif temperature < low and lowTemperature == False:
            blynk.notify(lowError)
            lowTemperature = True
        elif temperature > low and temperature < high:
            highTemperature = False
            lowTemperature = False
    except TypeError:
        print("TypeError in warnTemperature, check previous temperature value")

        

while True:
    blynk.run()  # runs blynk read/listen handlers, and establishes connection
    temperature = getTemperature()
    humidity = getHumidity()
    print("T",temperature, "H:",humidity)
    warnHumidity(30,65)
    warnTemperature(72,75)
    time.sleep(2)
    


################main################

    