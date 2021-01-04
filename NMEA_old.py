"""
class epoch:
    def __init__(self, NMEA):
        pass
    
    def new(self, NMEA):
        print(NMEA)
        if NMEA[0][3:] == "GGA":
            import datetime
            self.time = datetime.time(int(NMEA[1][0:2]), int(NMEA[1][2:4]), int(NMEA[1][4:6]))
        else:
            print("other")
        self.lat = 0
        self.lon = 0
"""
def Time(GGAList):
    timeElement = GGAList[1]
    import datetime
    hours = int(timeElement[0:2])
    minutes = int(timeElement[2:4])
    seconds = int(timeElement[4:6])
    GGAtime = datetime.time(hours, minutes, seconds)
    #print(GGAtime)
    return GGAtime

def Position(GGAList):
    latitudeElement = GGAList[2]
    latitudeCoordinate = float(latitudeElement[0:2])
    latitudeCoordinate = latitudeCoordinate + float(latitudeElement[2:])/60
    longitudeElement = GGAList[4]
    longitudeCoordinate = float(longitudeElement[0:3])
    longitudeCoordinate = longitudeCoordinate + float(longitudeElement[3:])/60
    height = float(GGAList[9])
    GGAposition = [latitudeCoordinate, longitudeCoordinate, height]
    return GGAposition

def GGA(GGAList):
    if GGAList[6] == '1':
        GGAtime = Time(GGAList)
        GGAposition = Position(GGAList)
        GGAnsat = int(GGAList[7])
        GGAHDOP = float(GGAList[8])
        GGAvalid = int(GGAList[6])
        GGAgeoid = float(GGAList[11])
        GGAdata = [GGAtime, GGAposition[0], GGAposition[1], GGAposition[2], GGAnsat, GGAHDOP, GGAgeoid, GGAvalid]
        return GGAdata
    if GGAList[6] == '0':
        if GGAList[1] == '':
            GGAnofix = 'No satellites'
        else:     
            GGAtime = timeTranslation(GGAList)
            GGAnsat = int(GGAList[7])
            GGAvalid = int(GGAList[6])
            GGAnofix =  [GGAtime, [], [], [], GGAnsat, [], [], GGAvalid]
        return GGAnofix
    
def VTG(VTGList):
    if VTGList[9][0] == 'N':
        return "no speed"
    else:   
        VTGtruedir = float(VTGList[1])
        VTGmagdir = float(VTGList[3])
        VTGspeedknots = float(VTGList[5])
        VTGspeedkph = float(VTGList[7])
        VTGmode = VTGList[9][0]
        VTGdata =  [VTGtruedir, VTGmagdir, VTGspeedknots, VTGspeedkph, VTGmode]
        return VTGdata