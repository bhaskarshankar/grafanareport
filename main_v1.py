import datetime
import json
import os
import re
import time
import urllib.request

import wget

from parsejson import parse_json_recursively
# from worddoc import *
from worddoc import createreport


def converttime(querystring , testlist) :
    res = querystring.split ( '&' )
    tofilter = filter ( lambda a : 'to=' in a , res )
    fromfilter = filter ( lambda a : 'from=' in a , res )

    tempto = (list ( tofilter ))
    tempfrom = (list ( fromfilter ))
    convertListto = ' '.join ( [ str ( e ) for e in tempto ] )
    convertListfrom = ' '.join ( [ str ( e ) for e in tempfrom ] )
    print ( convertListto )
    print ( convertListfrom )

    if "now" in convertListto :
        tolist = convertListto


    else :
        datetinme = convertListto.split ( '=' )
        temp1 = int ( datetinme [ 1 ] )
        type ( temp1 )
        converted_num = int ( temp1 ) / 1000
        print ( converted_num )
        tolist = str ( datetime.datetime.fromtimestamp ( converted_num ) )


    if "now" in convertListfrom :
        fromlist = convertListfrom


    else :
        datetinme = convertListfrom.split ( '=' )
        temp1 = int ( datetinme [ 1 ] )
        type ( temp1 )
        converted_num = int ( temp1 ) / 1000
        print ( converted_num )
        fromlist = str ( datetime.datetime.fromtimestamp ( converted_num ) )

    testlist.append ( ("TestDuration" , fromlist + " " + tolist) )
    return testlist


def grafanareport(hostname , querystring , file_path , dashboardname , testlist) :

    print(testlist,"printTestlist-before")
    converttime ( querystring , testlist )
    print ( testlist,"printTestlist-after" )

    # load data using Python JSON module
    regex = re.compile ( '[^a-zA-Z]' )
    dict1 = {}
    hostname = hostname
    dashboardname = dashboardname
    jsonapi = "api/dashboards/db/"
    jsonurl = "http://" + hostname + "/" + jsonapi + dashboardname
    imageurl = "http://" + hostname + "/render/dashboard-solo/db/" + dashboardname + "?orgId=1&theme=light&" + querystring + "&width=1500&height=350&panelId="
    print ( "jsonurl" )

    downloadloc = "images\\"

    for f in os.listdir ( downloadloc ) :
        os.remove ( os.path.join ( downloadloc , f ) )

    def downloadimage(dict1) :
        print ( dict1 )
        for k , v in dict1.items ( ) :
            print ( "downloadimage  {} name {} ".format ( k , v ) )

            # path = k
            path = regex.sub ( '' , k )
            print ( v )
            if type ( v ) == list :
                print ( "list" )
                for i in v :
                    pid = i
                    url = imageurl + str ( pid )
                    wget.download ( url , downloadloc + path + "_" + str ( pid ) + ".png" )
            else :
                pid = v
                url = imageurl + str ( pid )
                print ( url )
                wget.download ( url , downloadloc + path + "_" + str ( pid ) + ".png" )

    #def has_hidden_attribute(filepath) :
     #   return bool ( os.stat ( filepath ).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN )

    # fetch panel ID from jsonURL :
    with urllib.request.urlopen ( jsonurl ) as url :
        data = json.loads ( url.read ( ).decode ( ) )
        # calling function from parsejson.py
        dict1 = parse_json_recursively ( data , "id" )

    start_time = time.time ( )
    downloadimage ( dict1 )
    duration = time.time ( ) - start_time
    print ( f"Downloaded {len ( dict1 )} in {duration} seconds" )
    dict1.clear ( )
    createreport ( downloadloc , file_path , testlist )
    testlist.clear ( )

    for f in os.listdir ( downloadloc ) :
        os.remove ( os.path.join ( downloadloc , f ) )
