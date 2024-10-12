from machine import Pin
from machine import Pin,ADC
#import RPi.GPIO as GPIO
import dht
import machine
import urequests
import network, time
import dht11
import utime


HTTP_HEADERS = {'Content-Type': 'application/json'} 
THINGSPEAK_WRITE_API_KEY = '*****************'  
THINGSPEAK_Read_API_KEY = '******************'

channel_id = "*******"
field_number = "*"

ssid ='***************'
password ='*********'

led_net = machine.Pin(13, machine.Pin.OUT)
led_rp = machine.Pin(14, machine.Pin.OUT)

led_rp.value(1)

# Configure Pico W as Station
sta_if=network.WLAN(network.STA_IF)
sta_if.active(True)
 
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.connect(ssid, password)
    while not sta_if.isconnected(): pass
print('network config:', sta_if.ifconfig()[0])
led_net.value(1)

def read_field_data():
    response = urequests.get("https://api.thingspeak.com/channels/{}/fields/{}/last.json?api_key={}".format(channel_id, field_number, THINGSPEAK_Read_API_KEY))
    data = response.json()['field{}'.format(field_number)]
    response.close()
    return data

# Configuration du GPIO pour le relay
relais = machine.Pin(11, machine.Pin.OUT)

# Configuration du GPIO pour le capteur de l'humidité de sol
hum_sol=ADC(Pin(28))

# Configuration du GPIO pour le capteur de mouvement
pir = Pin(16, Pin.IN)

# Configuration du GPIO pour buzzer
buzzer= Pin(15, Pin.OUT)

# Configuration du GPIO pour le photoresistor
ldr_pin = Pin(26)
ldr_adc = ADC(ldr_pin)

# Configuration du GPIO pour le capteur DHT11
dht11 = dht.DHT11(machine.Pin(5))

# Seuil de luminosité pour distinguer le jour de la nuit
threshold = 500

buzzer.value(0)
relais.value(0)
while True:
   try:
        dht11.measure()
        temperature = dht11.temperature()
        humidity = dht11.humidity()
        print('Temperature: {}C'.format(temperature))
        print('Humidity: {}%'.format(humidity))
   except OSError as e:
        print('Failed to read sensor.')
        print('Error:', e)
        
 # Lire la valeur de luminosité du capteur LDR
   ldr_value = ldr_adc.read_u16()

    # Déterminer si c'est le jour ou la nuit
   if ldr_value > threshold:
        print("Il fait jour. Luminosité =", ldr_value)
   else:
        print("Il fait nuit. Luminosité =", ldr_value)


# Si le capteur détecte un mouvement, imprimer "Mouvement détecté"
   if pir.value() == 1:
        x=1
        print('Mouvement détecté={:.0f} '.format(x))
        buzzer.value(1)
   else:
        x=0
        print('Mouvement non détecté={:.0f} '.format(x))
        buzzer.value(0)
            
   print("hum_sol: " + str(hum_sol.read_u16()))
   data_1=hum_sol.read_u16()
   
   
   data = read_field_data()
   print("Latest data from field {}: {}".format(field_number, data))
    
   if data == '1':
        relais.value(1)
        print('relais ON')
   else:
        relais.value(0)
        print('relais OFF')
   
   time.sleep(10)
   
   msg_to_send = {'field1':temperature,'field2':humidity,'field3':ldr_value,'field4':x,'field5':data_1}
   #msg_to_send_1 ={'field3':ldr_value,'field4':x,'field5':data_1}
   request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY, json =msg_to_send, headers = HTTP_HEADERS )
   #request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY, json = msg_to_send_1, headers = HTTP_HEADERS )
   print('données envoyer  :)')
   request.close() 



