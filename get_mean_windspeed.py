"""
Gets the mean windspeed from the weewx database using during a user specified
interval.

At the moment the db location is hard-coded which is not ideal. #fixme
"""
import sqlite3
from sqlite3 import Error
import datetime
import sys
import pytz
from math import tan, atan2, sin, cos, pi, radians, degrees

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None
 
def degrees_to_cardinal(d):
    '''
    note: this is highly approximate...
    '''
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

def select_all_tasks(conn, timestart, timeend):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT windSpeed,windDir FROM archive where dateTime >\
                  {timestart} and dateTime < {timeend}")
 
    rows = cur.fetchall()
 
    return rows

def calc_aves(winds):
    """Calculates vector average wind speeds from the list of tuples
    """
    #define east west and north south components
    NS = 0.0
    EW = 0.0
    for item in winds:
        #print(item[0] * cos(radians(item[1])))
        NS += item[0] * cos(radians(item[1]))
        #print(item[0] * sin(radians(item[1])))
        EW += item[0] * sin(radians(item[1]))
    
    mag = (NS**2 + EW**2)**0.5 / len(winds)
    ang = degrees(atan2(EW,NS))
    return(mag,ang)


def main():

    #check argv for three arguments, expecting DD/MM/YY HH:MM MM
    assert len(sys.argv) == 4, f"Error expecting three command line arguments \
        got {len(sys.argv)}"
    #Weewx db location

    userdate = datetime.datetime.strptime(sys.argv[1] + " " 
                        +sys.argv[2], "%d/%m/%y %H:%M")  
    #adjust to utc
    #userdate = userdate - datetime.timedelta(0)                                   
    racemins = datetime.timedelta(minutes = int(sys.argv[3]))    

    userdateend = int((userdate + racemins).timestamp())
    userdate = int(userdate.timestamp())

    print(userdate)
    print(userdateend)

    knot_2_mile = 0.868976
    fname = r"/Volumes/files/MPYC/weatherstationdb/weewx.sdb"
    dbconn = create_connection(fname)
    rows = select_all_tasks(dbconn, userdate, userdateend)
    print(rows)
    results = calc_aves(rows)
    print(results)
    print(f"Race average wind speed: {results[0]* knot_2_mile} knots")
    print(f"Race average wind direction: {degrees_to_cardinal(results[1])} ({results[1]})")


    






if __name__ == "__main__":
    main()