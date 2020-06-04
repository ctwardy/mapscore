#!/usr/bin/env python3
# weather.py

"""
SARBayes weather.py
Jonathan Lee
================================================================================
The purpose of this module is to provide access to historic weather data using 
the API of the National Climate Data Center (NCDC).

The API provides the following endpoints: 
  * datasets
  * datacategories
  * datatypes
  * locationcategories
  * locations
  * stations
  * data

Every call to the API yields JSON data, with one key for results and the other 
for metadata like so: 

{
    "results": ..., 
    "metadata": {
        "resultset": {
            "limit": ..., 
            "count": ..., 
            "offset": ...
        }
    }
}

The maximum number of results that can be requested per call is 1000. The 
default limit is 25 items.
================================================================================
"""

NOTES = """
Each measurement is associated with a datatype. For example, TMAX is the maximum temperature of the given time range in tenths of a degree Celsius. I have tried to determine which datatypes were needed for filling in ISRID (see the tuple needed_datatypes in function get_conditions), but it is possible that there may be better datatypes that I have missed (there are about 1500 of them, and many of these are outdated and no longer recorded).

Given a date and a location, the module can query for stations that supported the GHCND dataset, were available at given date, and are located within a certain bounding box. It then goes through each station, requests what it knows, and determines which data are relevant and to be returned. Currently, it is not possible to search by datatypes, which slows down data collection considerably (see the note). Also, the size of the bounding box is only a rough estimate. More testing will be needed.
"""

import urllib.request, urllib.parse
import geopy
import json
from math import pi, sin, cos, asin, degrees, radians

API_URL = 'http://www.ncdc.noaa.gov/cdo-web/api/v2/{}?{}'
API_TOKEN = 'CAKlHptoFxCtALqpfyjIKtmpfCbQIWse'

R = 6371 # Earth's radius in km


def request_data(endpoint, safe=':,', **parameters):
    """ Build a URL, fetch the data, and return that data in JSON format. """
    url = API_URL.format(endpoint, 
        urllib.parse.urlencode(parameters, safe=safe))
    request = urllib.request.Request(url, headers={'token': API_TOKEN})
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


def get_bounds(coordinates, d):
    """ Get the southwest and northeast coordinates of a bounding box.

    @param coordinates = sequence [latitude, longitude] in decimal degrees
    @param d = width of the box, in km (float)
    
        Sources: 
          * http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
          * https://github.com/jfein/PyGeoTools/blob/master/geolocation.py
    """
    lat = radians(coordinates.latitude)
    lon = radians(coordinates.longitude)
    r = d/R
    
    lat_min, lat_max = lat - r, lat + r
    # Special case: poles
    if abs(lat_min) > pi/2:
        lon_min, lon_max = -pi, pi
        lat_min, lat_max = max(lat_min, -pi/2), min(lat_max, pi/2)
    else:
        change_lon = asin(sin(r)/cos(lat))
        lon_min, lon_max = lon - change_lon, lon + change_lon
        if lon_min < -pi:
            lon_min += 2*pi
        if lon_max > pi:
            lon_max -= 2*pi
    
    return (
        geopy.Point(degrees(lat_min), degrees(lon_min)), 
        geopy.Point(degrees(lat_max), degrees(lon_max))
    )


def get_stations(date, coordinates, datasetid='GHCND', d=20):
    """ Get the data of the weather stations available at the given date and 
        coordinates within a bounding box with sides of length 2d.
    """
    date_as_str = date.date().isoformat()
    sw, ne = get_bounds(coordinates, d)
    extent = ','.join(
        str(n) for n in [sw.latitude, sw.longitude, ne.latitude, ne.longitude])
    data = request_data(
        'stations', 
        datasetid=datasetid, 
        startdate=date_as_str, 
        enddate=date_as_str, 
        extent=extent
    )
    yield from data['results']


def get_conditions(date, coordinates):
    """ Get the general conditions at a given date and location.
        Returns as a tuple: 
          * Maximum temperature (tenths of degrees C)
          * Minimum temperature (tenths of degrees C)
          * Average daily wind speed (m/s)
          * Storm total precipitation
          * Snowfall (mm)
    """
    date_as_str = date.date().isoformat()
    # Order needs to be maintained (no dictionary)
    needed_datatypes = ['TMAX', 'TMIN', 'AWND', 'NTP', 'SNOW']
    needed_values = [None] * len(needed_datatypes)
    
    # Normally, the data could be all obtained in a few call, but the API's 
    # instructions to separate the station IDs with ampersands seems to not 
    # work because they are interpreted as part of the URL's GET parameters.
    # URL encoding those ampersands also doesn't seem to work.
    # For now, make individual requests to each station, but sleep in the loop 
    # so that the server doesn't shut us out for spamming requests.
    
    from time import sleep # Temporary hack
    
    for station in get_stations(date, coordinates):
        data = request_data(
            'data', 
            datasetid='GHCND', 
            startdate=date_as_str, 
            enddate=date_as_str, 
            stationid=station['id'], 
            limit=1000
        )
        
        if 'results' in data:
            for measurement in data['results']:
                datatype = measurement['datatype'].strip()
                if datatype in needed_datatypes:
                    index = needed_datatypes.index(datatype)
                    if needed_values[index] is None:
                        needed_values[index] = measurement['value']
                        print('Updated:', needed_values)
                        if None not in needed_values:
                            return needed_values
        
        sleep(1) # Temporary hack
    else:
        return needed_values # Some of the data were not able to be obtained


import datetime
date = datetime.datetime(2015, 4, 10, 0, 0, 0)
coordinates = geopy.point.Point(38.845432, -77.320955)
print(get_conditions(date, coordinates))
