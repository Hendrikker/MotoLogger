def createGPX(data, savefile):
    import gpxpy
    import gpxpy.gpx

    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    for dataline in data:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(dataline[0][1],
                                                          dataline[0][2],
                                                          elevation=dataline[0][3]))

    # You can add routes and waypoints, too...
    gpx_str = gpx.to_xml()
    #print('Created GPX:', gpx.to_xml())
    print(gpx_str)
    file = open(savefile, 'w')
    file.write(gpx_str)
    file.close()
