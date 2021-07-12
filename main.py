import blynklib
import random
import adafruit_dht
import board
import os
import sys
import subprocess
import time
from picamera import PiCamera
from datetime import datetime
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# TODO
# error handling for when first reading fails:DONE
# test on Pi zero instead of Pi 4
# if Pi zero has issues, use a for loop inside the while loop to impliment an average, while also still utilizing the sleep function
# impliment error logging
# COPY function that handles pin 4. Impliment as true false instead of integer. Use with button to email photo


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

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)
# file1 = drive.CreateFile({'title': 'Hello.txt'})
# file1.SetContentString('Hello World')
# file1.Upload()

#EMAIL
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = 'tamugreenhousesensors@gmail.com'
GMAIL_PASSWORD = 


BLYNK_AUTH = 'k23bFgoarBaCRdw7BxUTivijuj7Gatk0' #use your auth token here
blynk = blynklib.Blynk(BLYNK_AUTH)

DHT_PIN = 4
dht_device = adafruit_dht.DHT22(board.D4)
Celcius = 0
temperature = 0
humidity = 0

# these variables are used in warning functions to prevent the app from notifying for out of range data more than once while it is out of range
highHumidity = False
lowHumidity = False
lowTemperature = False
highTemperature = False

limit = 0  # this will become one of the temp/humid range limiting variables later
pictureRequest = False
sensorName = "Greenhouse_1"

####################functions#####################

# read_virtual_pin_handler functions respond to virtual pins on the app requesting data
# these functions do not pull data from the app despite their names
READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"
@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):
    
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, temperature)
    

@blynk.handle_event('read V1')
def read_virtual_pin_handler(pin):
    
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, humidity)
   
# write_virtual_pin_handler functions will read data from a virtual pin from the app
WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_PIN_EVENT] Pin: V{} Value: '{}'"
# register handler for virtual pin V4 write event
@blynk.handle_event('write V4')
def write_virtual_pin_handler(pin, value):
    #print(WRITE_EVENT_PRINT_MSG.format(pin, value))
    # can I put a mutex lock here?
    print(int(value[0]))
    global limit
    limit = int(value[0])
    
@blynk.handle_event('write V5')    
def write_virtual_pin_handler(pin, value):
    #print(WRITE_EVENT_PRINT_MSG.format(pin, value))
    # can I put a mutex lock here?
    print('pictureRequest button = ' + str(bool(value[0])))
    global pictureRequest
    pictureRequest = bool(value[0])

# Retrieves temperature data and optionally pushes to supergraph on pin V2
# hardware is prone to fail every few readings, in those cases tempurature is not changed and returned as it was before via the except blocks
def getTemperature():
    global temperature
    try:
        Celcius = dht_device.temperature
        temperature = (Celcius * 9/5)+32
        # blynk.virtual_write(2, temperature)
        return temperature
    except RuntimeError:
        print("error with temperature reading")
        return temperature
    except TypeError:
        print("try again")
        return temperature

# Retrieves humidity data and optionally pushes to supergraph on pin V3
def getHumidity():
    global humidity
    try:
        humidity = dht_device.humidity
        blynk.virtual_write(3, humidity)
        return humidity
    except RuntimeError:
        print("error with humidity reading")
        return humidity

# detects if humidity is outside of the given range and tells blynk to send a push notification
def warnHumidity(low, high):
    lowError = "Humidity below " + str(low) + " detected"
    highError = "Humidity above " + str(high) + "% detected"
    global lowHumidity
    global highHumidity
    try:
        if humidity > high and highHumidity == False:
            blynk.notify(highError)
            highHumidity = True
        elif humidity < low and lowHumidity == False:
            blynk.notify(lowError)
            lowHumidity = True
        elif humidity < high and humidity > low:
            highHumidity = False
            lowHumidity = False
    except:
        print("error in warnHumidity")

# detects if temperature is outside of the given range and tells blynk to send a push notification
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

def namePicture():
    global sensorName
    name = sensorName + str(datetime.now())
    return name

def takePicture():
    camera = PiCamera()
#    #camera.start_preview()
#    #time.sleep(1)
    photoName = '/home/pi/Desktop/'+namePicture()+'.jpg'
    camera.capture(photoName)
    print('photo taken')
    camera.close()
    sendEmail('tamugreenhousesensors@gmail.com', 'Test', 'test',photoName)
    time.sleep(2)
#     try:
#         #camera.start_preview()
#         #time.sleep(1)
#         camera.capture('/home/pi/Desktop/'+namePicture()+'.jpg')
#         print('photo taken')
#     except:
#         print("camera error")
#     finally:
#         camera.stop_preview()
#         time.sleep(2)

def sendEmail(recipient, subject, content, image):
    global GMAIL_USERNAME
    #Create Headers
    emailData = MIMEMultipart()
    emailData['Subject'] = subject
    emailData['To'] = recipient
    emailData['From'] = GMAIL_USERNAME
    
    emailData.attach(MIMEText(content))
    
    imageData = MIMEImage(open(image, 'rb').read(), 'jpg')
    imageData.add_header('Content-Disposition', 'attachement; filename="image.jpg"')
    emailData.attach(imageData)
    
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo()
    
    session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
    
    session.sendmail(GMAIL_USERNAME, recipient, emailData.as_string())
    session.quit
    
syncCounter = 0
pictureCounter = 0
########################main########################

while True:
    blynk.run()  # runs blynk read/listen handlers, and establishes connection
    temperature = getTemperature()
    humidity = getHumidity()
    print("T",temperature, "H:",humidity)
    print("limit", limit)
    warnHumidity(30,65)
    warnTemperature(72,75)
    time.sleep(2)
    # this block fixes an issue where data set on the app was not being recieved on the hardware. Can be put into a function later
    if syncCounter == 2:
        blynk.virtual_sync(4)
        blynk.virtual_sync(5)
        syncCounter = 0
    # This block dictates how often a photo is taken
    if pictureRequest == True:
        try:
            takePicture()
            blynk.virtual_write(5,0)
            pictureRequest = False
        except:
            print("error with takePicture()")
        #pictureCounter = 0
        
            
        
        
    syncCounter += 1
    #pictureCounter += 1
    