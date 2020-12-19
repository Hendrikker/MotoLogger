# imports
from datetime import datetime
from gpiozero import *
import RPi.GPIO as GPIO
from subprocess import check_call
import time
import os
import serial
import NMEA
import export

# initialize serial port for gps
os.system("sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
port = "/dev/serial0"
serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)

# output
now = datetime.now()
now_string = now.strftime("%d%m%Y_%H%M%S")
datafolder = "/home/pi/MotoLoggerV2/data/"
savefile = datafolder + now_string + ".txt"
print("file: " + savefile)
file=open(savefile, 'w')
file.close()

#
active = True
savesat = False

if savesat == True:
    satsavefile = datafolder + now_string + "_sats.txt"

# elements
red = LED(27)
white = LED(22)
green = LED(17)
iobutton = Button(24)
iolight = LED(18)
shutdown_btn = Button(7, hold_time=1)

# events functions
# logging button start
def start():
    print("start")
    iolight.on()
    #white.blink()
# logging button stop
def stop():
    print("stop")
    iolight.off()
    #white.off()
# Shutdown
def shutdown():
    global active
    active = False
    print("shutdown")

iobutton.when_released = start
iobutton.when_pressed = stop
shutdown_btn.when_held = shutdown
green.on()

started = False

try:
    while active == True:
        green.on()
        #time.sleep(0.5)
        if iobutton.is_pressed:
            pass
        else:
            # GPS reading
            serialData = serialPort.readline()
            nmea = ["-"]
            try:
                nmea = serialData.decode('utf-8').split(',')
            except:
                print("decode error")
            if nmea != "-":
                nmeatype =  nmea[0][3:]
                #print(nmea)
                """
                epoch = [time,
                        lattitude,
                        longitude,
                        altitude,
                        bearing,
                        speed,
                        ,
                        geoid,
                        #satelites,
                        HDOP,
                        VDOP,
                        PDOP,
                        Fix
                        ]
                """
                if started == True and nmeatype == 'GGA':
                    if epoch[0] != "":
                        print(epoch)
                        white.on()
                        line = ",".join(epoch) + "\n"
                        file=open(savefile, 'a')
                        file.write(line)
                        file.close()
                    if savesat == True and sats[0] != None:
                        satline = ",".join(sats) + "\n"
                        satfile=open(satsavefile, 'a')
                        satfile.write(satline)
                        satfile.close()
                        
                    #print("epoch saved")
                    
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
                
                
                if started == True and nmeatype == "GSV" and savesat == True:
                    #print("processing GSA: " + nmea[0][1:3])
                    #print(nmea)
                    for i in list(range(4,len(nmea)-1,4)):
                        PRN = nmea[i]
                        if PRN != '':
                            SV_type = nmea[0][1:3]
                            sats.append(SV_type)
                            sats.append(PRN)
                            ele = nmea[i+1]
                            sats.append(ele)
                            azi = nmea[i+2]
                            sats.append(azi)
                            SNR = nmea[i+3].split('*')
                            sats.append(SNR[0])
                        
                    
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
    #export.GEOJSON(GGA, "data/"+savefile+"_GGA")
    #export.GPX(GGA, "data/"+savefile)
    #GPIO.setmode(GPIO.BCM)
    white.off()
    green.off()
    red.on()
    time.sleep(1)
    red.off()
    #check_call(['sudo', 'poweroff'])
    #GPIO.cleanup()
    
    
