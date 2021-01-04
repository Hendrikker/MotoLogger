# imports
from datetime import datetime
from gpiozero import *
import RPi.GPIO as GPIO
from subprocess import check_call
import time
import os
import serial
import export
import NMEA

# output
now = datetime.now()
now_string = now.strftime("%d%m%Y_%H%M%S")
mainfolder = "/home/pi/"
datafolder = mainfolder + "/MotoLoggerData/"
try:
    os.mkdir(datafolder)
except FileExistsError:
    pass
timefolder = datafolder + now_string + "/"
os.mkdir(timefolder)
savefile = timefolder + now_string + ".txt"
print("file: " + savefile)
file=open(savefile, 'w')
file.write("Time of Day,Lattitude,Longitude,Altitude,Bearing,Speed,Empty,Geoid,Number of Satellites,HDOP,VDOP,PDOP,FIX\n")
file.close()

# Activity booleans
active = True
savesat = False
if savesat == True:
    satsavefile = timefolder + now_string + "_sats.txt"

# elements
red = LED(27)
white = LED(22)
green = LED(17)
iobutton = Button(24)
iolight = LED(18)
shutdown_btn = Button(7, hold_time=1)

# initialize serial port for gps
#os.system("sudo systemctl stop gpsd.socket")
os.system("sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock")
port = "/dev/ttyAMA0"
#/dev/serial0
serialPort = serial.Serial(port, baudrate = 9600)#, timeout = 0.1)
#time.sleep(20)

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
epoch = ['']*13
sats = [None]
try:
    while active == True:
        green.on()
        nmea = ["-"]
        try:
            serialData = serialPort.readline()
        except:
            pass
        if iobutton.is_pressed:
            pass
        else:
            try:
                nmea = serialData.decode('utf-8').split(',')
                red.off()
            except:
                print("decode error")
            if nmea != "-":
                NMEA.Read(nmea)

                """
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
                    if savesat == True and sats[0] != None:
                        #satline = ",".join(sats) + "\n"
                        #satfile=open(satsavefile, 'a')
                        #satfile.write(satline)
                        #satfile.close()
                        pass 
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
                    """
finally:
    white.off()
    green.off()
    red.on()
    export.LOGtoGPX(savefile)
    export.LOGtoGEOJSON(savefile)
    #export.SATtoJSON(satsavefile)
    time.sleep(0.5)
    red.off()
    #check_call(['sudo', 'poweroff'])
    #GPIO.cleanup()
    
    
