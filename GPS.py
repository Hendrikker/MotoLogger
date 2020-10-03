def timeTranslation(GPGGAList):
    timeElement = GPGGAList[1]
    import datetime
    hours = int(timeElement[0:2])
    minutes = int(timeElement[2:4])
    seconds = int(timeElement[4:6])
    GPStime = datetime.time(hours, minutes, seconds)
    #print(GPStime)
    return GPStime

def positionTranslation(GPGGAList):
    latitudeElement = GPGGAList[2]
    latitudeCoordinate = float(latitudeElement[0:2])
    latitudeCoordinate = latitudeCoordinate + float(latitudeElement[2:])/60
    longitudeElement = GPGGAList[4]
    longitudeCoordinate = float(longitudeElement[0:3])
    longitudeCoordinate = longitudeCoordinate + float(longitudeElement[3:])/60
    height = float(GPGGAList[9])
    GPSposition = [latitudeCoordinate, longitudeCoordinate, height]
    return GPSposition

def dataTranslation(GPGGAList):
    if GPGGAList[6] == '1':
        GPStime = timeTranslation(GPGGAList)
        GPSposition = positionTranslation(GPGGAList)
        GPSnsat = int(GPGGAList[7])
        GPSHDOP = float(GPGGAList[8])
        GPSvalid = int(GPGGAList[6])
        GPSgeoid = float(GPGGAList[11])
        GPSdata = [GPStime, GPSposition[0], GPSposition[1], GPSposition[2], GPSnsat, GPSHDOP, GPSgeoid, GPSvalid]
        return GPSdata
    if GPGGAList[6] == '0':
        if GPGGAList[1] == '':
            GPSnofix = 'No satellites'
        else:     
            GPStime = timeTranslation(GPGGAList)
            GPSnsat = int(GPGGAList[7])
            GPSvalid = int(GPGGAList[6])
            GPSnofix =  [GPStime, [], [], [], GPSnsat, [], [], GPSvalid]
        return GPSnofix