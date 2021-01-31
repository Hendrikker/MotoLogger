import RPi.GPIO as GPIO
from gpiozero import LED, Button
import time
from datetime import datetime
import os
import serial
import export
import NMEA

started = False
epoch = ['']*13
active = True
savesat = False

savefile = export.createfile()

# initialize serial port for gps
os.system("sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
port = "/dev/ttyAMA0"
serialPort = serial.Serial(port, baudrate = 9600)#, timeout = 0.1)
#time.sleep(20)

red = LED(23)
green = LED(24)
iobutton = Button(17)
offbutton = Button(5)

def start():
    print("start")
def stop():
    print("stop")
def shutdown():
    global active
    active = False
    print("shutdown")
    
iobutton.when_released = stop
iobutton.when_pressed = start
offbutton.when_held = shutdown

try:
    while active == True:
        green.on()
        nmea = ["-"]
        try:
            serialData = serialPort.readline()
        except:
            pass
        if not iobutton.is_pressed:
            pass
        else:
            try:
                nmea = serialData.decode('utf-8').split(',')
                red.off()
            except:
                print("decode error")
            if nmea != "-":
                #NMEA.Read(nmea)
                nmeatype =  nmea[0][3:]
                #print(nmea)
                if started == True and nmeatype == 'GGA':
                    if epoch[0] != "":
                        print(epoch)
                        white.on()
                        line = ",".join(epoch) + "\n"
                        file=open(savefile, 'a')
                        file.write(line)
                        file.close()
                if nmeatype == "GGA":
                    #print("processing GGA")
                    #print(nmea)
                    epoch = ['']*13
                    sats = [None]
                    if nmea[6] == '0':
                        pass
                    else:
                        started = True
                        # time
                        timeline = ":".join([nmea[1][0:2], nmea[1][2:4], nmea[1][4:6]])
                        epoch[0] = timeline
                        sats[0] = timeline
                        
                        # lattitude
                        lat = float(nmea[2][0:2]) + float(nmea[2][2:])/60
                        epoch[1] = str(lat)
                        
                        # longitude
                        lon = float(nmea[4][1:3]) + float(nmea[4][3:])/60
                        epoch[2] = str(lon)
                        
                        # altitude
                        alt = float(nmea[9])
                        epoch[3] = str(alt)
                                            
                        # geoid
                        geoid = float(nmea[11])
                        epoch[7] = str(geoid)
                        
                        # number of satell
                        nsat = int(nmea[7])
                        epoch[8] = str(nsat)
                        
                        # Horizontal Dilution of Precision
                        HDOP = float(nmea[8])
                        epoch[9] = str(HDOP)
                        
                        # Fix
                        fix = int(nmea[6])
                        epoch[12] = str(fix)
                        
                if started == True and nmeatype == "GSA":
                    #print("processing GSA: ")
                    #print(nmea)
                    PDOP = nmea[15]
                    epoch[11] = PDOP
                    
                    HDOP = nmea[16]
                    epoch[9] = HDOP
                    
                    VDOP = nmea[17].split('*')
                    epoch[10] = VDOP[0]     
                    
                if started == True and nmeatype == "VTG":
                    #print("processing VTG")
                    #print(nmea)
                    # directiont relative to true North
                    bearing = nmea[1]
                    epoch[4] = bearing
                    
                    # speed over ground in kph
                    speed = nmea[7]
                    epoch[5] = speed
finally:
    green.off()
    red.on()
    export.LOGtoGPX(savefile)
    time.sleep(0.5)
    red.off()
    GPIO.cleanup()
    