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
    cur.execute(f"SELECT avg(windSpeed),avg(windDir) FROM archive where dateTime >\
                  {timestart} and dateTime < {timeend}")
 
    rows = cur.fetchall()
 
    return rows

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
    print(f"Race average wind speed: {rows[0][0]* knot_2_mile} knots")
    print(f"Race average wind direction: {degrees_to_cardinal(rows[0][1])} ({rows[0][1]})")


    






if __name__ == "__main__":
    main()