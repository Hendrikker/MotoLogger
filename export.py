#import datetime
#data = [[datetime.time(18, 7, 21), 51.996803166666666, 4.354635, 110.9, 6, 1.33, 45.9, 1,
#             1.0126953125, -0.016357421875, -0.044677734375, -0.7786259541984732, -0.16793893129770993, -0.3511450381679389],
#            [datetime.time(18, 7, 22), 51.9968085, 4.354642166666666, 110.5, 6, 1.33, 45.9, 1,
#             1.003662109375, -0.042236328125, -0.032470703125, -0.7557251908396947, -0.22900763358778625, -0.35877862595419846]]
def exportGPX(data, savefile):
    import xml.etree.cElementTree as ET
    gpx = ET.Element("gpx", creator="MotoLogger", version="1.1")
    trk = ET.SubElement(gpx, "trk")
    trkseg = ET.SubElement(trk, "trkseg")
    for dataline in data:
        trkpt = ET.SubElement(trkseg, "trkpt", lat=str(dataline[1]), lon=str(dataline[2]))
        ele = ET.SubElement(trkpt, "ele")
        ele.text = str(dataline[3])
        geoid = ET.SubElement(trkpt, "geoidheight")
        geoid.text = str(dataline[6])
        fix = ET.SubElement(trkpt, "fix")
        fix.text = "3d"
        sat = ET.SubElement(trkpt, "sat")
        sat.text = str(dataline[4])
        hdop = ET.SubElement(trkpt, "hdop")
        hdop.text = str(dataline[5])

    tree = ET.ElementTree(gpx)
    tree.write(savefile+".gpx")

def exportGEOJSON(data, savefile):
    import json
    master = {"type":"FeatureCollection", "features":[]}
    linepoints = []
    for dataline in data:
        linepoints.append([dataline[1], dataline[2]])
        pointfeature = {"type":"Feature",
                   "geometry":{"type":"Point", "coordinates":[dataline[1], dataline[2]]},
                   "properties":{"elevation":dataline[3],
                                 "number of satellites":dataline[4],
                                 "hdop":dataline[5],
                                 "geoid height":dataline[6],
                                 "valid fix": dataline[7],
                                 "acceleration X":dataline[8],
                                 "acceleration Y":dataline[9],
                                 "acceleration Z":dataline[10],
                                 "gyro X":dataline[11],
                                 "gyro Y":dataline[12],
                                 "gyro Z":dataline[13]
                                 }
                   }
        master["features"].append(pointfeature)
        
    linefeature = {"type":"Feature",
                   "geometry":{"type":"LineString",
                               "coordinates":linepoints}}
    master["features"].append(linefeature)
    master_json = json.dumps(master)
    text_file = open(savefile + ".json", "w")
    text_file.write(master_json)
    text_file.close()
