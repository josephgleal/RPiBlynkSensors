import blynklib
import random
import adafruit_dht
import board

BLYNK_AUTH = 'k23bFgoarBaCRdw7BxUTivijuj7Gatk0' #use your auth token here
blynk = blynklib.Blynk(BLYNK_AUTH)

DHT_PIN = 4
dht_device = adafruit_dht.DHT22(board.D4)
Celcius = 0
temperature = 0
humidity = 0

READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"
@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):
    
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, temperature)
    

@blynk.handle_event('read V1')
def read_virtual_pin_handler(pin):
    
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, humidity)
    

while True:
    blynk.run()
    try:
        humidity = dht_device.humidity
        blynk.virtual_write(3, humidity)
    except RuntimeError:
        print("error with humidity reading")
    Celcius = dht_device.temperature
    temperature = (Celcius * 9/5)+32
    blynk.virtual_write(2, temperature)
    print("T",temperature, "H:",humidity)
    
    