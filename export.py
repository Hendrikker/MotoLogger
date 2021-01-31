def createfile():
    from datetime import datetime
    import os
    now = datetime.now()
    now_string = now.strftime("%d%m%Y_%H%M%S")
    mainfolder = "/home/pi/"
    datafolder = mainfolder + "MotoLoggerData/"
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
    return savefile

def LOGtoGPX(savefile, pretty=False):
    import xml.etree.ElementTree as ET
    ET.register_namespace('gpxtpx',"https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd")
    gpx = ET.Element("gpx", creator="MotoLogger", version="1.1", xmlns="http://www.topografix.com/GPX/1/1")
    meta = ET.SubElement(gpx, "metadata")
    meta_name = ET.SubElement(meta, "name")
    meta_name.text = "Titel"
    desc = ET.SubElement(meta, "desc")
    desc.text = "Bescrhijving van rit"
    author = ET.SubElement(meta, "author")
    author_name = ET.SubElement(author, "name")
    author_name.text = "Stijn Lodder"
    author_link = ET.SubElement(author, "link", href="http://www.stijnlodder.nl/Dashboard")
    meta_time = ET.SubElement(meta, "time")
    meta_time.text = "time"

    trk = ET.SubElement(gpx, "trk")
    trk_name = ET.SubElement(trk, "name")
    trk_name.text = "Titel"
    trkseg = ET.SubElement(trk, "trkseg")

    log = open(savefile, "r")
    header = log.readline()
    line = log.readline().split(',')
    while line != ['']:
        #print(line)
        trkpt = ET.SubElement(trkseg, "trkpt", lat=str(line[1]), lon=str(line[2]))
        ele = ET.SubElement(trkpt, "ele")
        ele.text = str(line[3])
        time = ET.SubElement(trkpt, "time")
        time.text = "time"
        #fix = ET.SubElement(trkpt, "fix")
        #fix.text = "3d"
        hdop = ET.SubElement(trkpt, "hdop")
        hdop.text = str(line[5])
        extensions = ET.SubElement(trkpt, "extensions")
        gpxtpx = ET.SubElement(extensions, "{https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd}TrackPointExtension")
        course = ET.SubElement(gpxtpx, "{https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd}course")
        course.text = str(line[4])
        speed = ET.SubElement(gpxtpx, "{https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd}speed")
        speed.text = str(line[5])
        line = log.readline().split(',')
    log.close()
    savefile = savefile.strip(".txt")
    tree = ET.ElementTree(gpx)
    if pretty == True:
        from xml.dom import minidom
        xmlstr = minidom.parseString(ET.tostring(gpx)).toprettyxml(indent="   ")
        gpxfile = open(savefile + ".gpx", "w")
        gpxfile.write(xmlstr)
        gpxfile.close()
    else:
        tree.write(savefile + ".gpx")

def LOGtoGEOJSON(savefile, pretty=False):
    import json
    master = {"type":"FeatureCollection", "features":[]}
    linepoints = []

    log = open(savefile, "r")
    header = log.readline()
    line = log.readline().split(',')
    while line != ['']:
        #print(line)
        coords = [float(line[2]), float(line[1])]
        linepoints.append(coords)
        pointfeature = {"type":"Feature",
                   "geometry":{"type":"Point", "coordinates":coords},
                   "properties":{"elevation":float(line[3]),
                                 "bearing": toFloat(line[4]),
                                 "speed":toFloat(line[5]),
                                 "nsat":int(line[8]),
                                 "HDOP":float(line[9]),
                                 "VDOP":float(line[10]),
                                 "PDOP":float(line[11]),
                                 "geoid":float(line[7]),
                                 "fix": line[12]
                                 }
                   }
        if (float(line[11])<=3):
            master["features"].append(pointfeature)
        line = log.readline().split(',')
    log.close()

    linefeature = {"type":"Feature",
                   "geometry":{"type":"LineString",
                               "coordinates":linepoints}}
    master["features"].append(linefeature)
    savefile = savefile.strip(".txt")
    text_file = open(savefile + ".json", "w")
    if pretty==True:
        text_file.write(json.dumps(master, sort_keys=True, indent=4))
    else:
        json.dump(master, text_file)
    text_file.close()

def SATtoJSON(savefile, pretty=False):
    import json
    sats = {}
    sats2 = {}

    log = open(savefile, "r")
    header = log.readline()
    line = log.readline().split(',')

    while line != ['']:
        line = log.readline().split(',')
        for i in list(range(1, len(line), 5)):
            ID = line[i] + line[i+1]
            if line[i+2] != "" and line[i+3] != "":
                epoch = [float(line[i+2]), float(line[i+3])]
                if ID not in sats.keys():
                    sats2[ID] = [epoch]
                    sats[ID] = {}
                    sats[ID]["Time"] = [line[0]]
                    sats[ID]["Elevation"] = [float(line[i+2])]
                    sats[ID]["Azimuth"] = [float(line[i+3])]
                    sats[ID]["SNR"] = [line[i+4].strip("\n")]
                else:
                    sats2[ID].append(epoch)
                    sats[ID]["Time"].append(line[0])
                    sats[ID]["Elevation"].append(float(line[i+2]))
                    sats[ID]["Azimuth"].append(float(line[i+3]))
                    sats[ID]["SNR"].append(line[i+4].strip("\n"))
    log.close()
    savefile = savefile.strip(".txt")
    text_file = open(savefile + ".json", "w")
    if pretty==True:
        text_file.write(json.dumps(sats, sort_keys=True, indent=4))
    else:
        json.dump(sats, text_file)
    text_file.close()
    
def toFloat(line):
    if len(line) == 0:
        return 0
    else:
        return float(line)

def SupplementSpeed(savefile):
    log = open(savefile, "r")
    header = log.readline()
    line = log.readline().split(',')

LOGtoGPX("F:/Projecten/MotoLogger/gpx test/26122020_161723.txt", True)
#LOGtoGEOJSON("./data/20122020_011103")
#SATtoJSON("./data/20122020_011103_sats", True)
