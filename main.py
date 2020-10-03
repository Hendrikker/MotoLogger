#MPU initials
import MPU
from time import sleep          #import
MPU.MPU_Init()

#GPS intials
import GPS
import os
os.system("sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
import serial
port = "/dev/serial0"
serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)

import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD
import time
# Raspberry Pi pin configuration:
lcd_rs        = 25
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 18
lcd_d7        = 22
lcd_backlight = 1
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2
# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)
lcd.message('Ready to Start\nPress button')

def button_callback(channel):
    from datetime import datetime
    global state
    if state == 0:
        now = datetime.now()
        now_str = now.strftime("%d%m%Y_%H%M%S")
        lcd.clear()
        lcd.message("Logging File:\n"+now_str)
        print(now_str)
    if state == 1:
        lcd.clear()
        lcd.message("Logging: \nInitializing")
    state += 1
    print(state)
            
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(16,GPIO.FALLING,callback=button_callback)

state = 0
data = []
try:
    while state <= 2:#MPU reading
        #print(state)
        if state == 0:
            time.sleep(0.1)
        if state == 1:
            try:
                # GPS reading
                serialData = serialPort.readline()
                serialDataList = serialData.decode('utf-8').split(',')
                # if there is GPS
                if serialDataList[0] == "$GPGGA":
                    print(serialDataList)
                    GPSdata = GPS.dataTranslation(serialDataList)
                    print(GPSdata)
                    # MPU reading
                    MPUdata = MPU.MPUreader()
                    print(MPUdata)
                    # Print on LCD
                    if GPSdata == 'No satellites':
                        lcd.clear()
                        lcd.message("Logging: NO FIX\n" + "No Time" + " Sats:" + str(0))
                    else:
                        if GPSdata[-1] == 0:
                            lcd.clear()
                            lcd.message("Logging: NO FIX\n" + GPSdata[0].strftime("%H:%M:%S") + " Sats:" + str(GPSdata[4]))
                        if GPSdata[-1] == 1:
                            lcd.clear()
                            lcd.message("Logging: FIX\n" + GPSdata[0].strftime("%H:%M:%S") + " Sats:" + str(GPSdata[4]))
                            dataline = []
                            dataline.append(GPSdata)
                            dataline.append(MPUdata)
                            data.append(dataline)
            except UnicodeDecodeError:
                print('Failed start, trying again.')
                pass
            except OSError:
                print('OSError')
                pass
finally:
    print('saving')
    lcd.clear()
    lcd.message("Logging: \nSaving ...")
    # saving
    import export
    from datetime import datetime
    now = datetime.now()
    now_str = now.strftime("%d%m%Y_%H%M%S")
    export.exportGPX(data, now_str)
    export.exportGEOJSON(data, now_str)
    lcd.clear()
    GPIO.cleanup()
    #print(data)