import blynklib
import random

BLYNK_AUTH = 'k23bFgoarBaCRdw7BxUTivijuj7Gatk0' #use your auth token here
blynk = blynklib.Blynk(BLYNK_AUTH)
READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"
@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, random.randint(0, 255))
    

while True:
    blynk.run()
    