import datetime
import json
import logging
import os
import re
import threading
import time
import urllib
from configparser import ConfigParser
from urllib.error import HTTPError
from urllib.request import urlretrieve

from log import logger
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
    # print ( convertListto )
    # print ( convertListfrom )

    if "now" in convertListto :
        tolist = convertListto


    else :
        datetinme = convertListto.split ( '=' )
        temp1 = int ( datetinme [ 1 ] )
        type ( temp1 )
        converted_num = int ( temp1 ) / 1000
        # print ( converted_num )
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
    # print ( testlist , "printTestlist-before" )
    logger.info ( "Converting Grafana timestamp to human readable format %s %s" , querystring , testlist )

    converttime ( querystring , testlist )
    # print ( testlist , "printTestlist-after" )

    # load data using Python JSON module
    regex = re.compile ( '[^a-zA-Z]' )
    # dict1 = {}
    hostname = hostname
    dashboardname = dashboardname
    jsonapi = "api/dashboards/db/"
    jsonurl = "http://" + hostname + "/" + jsonapi + dashboardname
    imageurl = "http://" + hostname + "/render/dashboard-solo/db/" + dashboardname + "?orgId=1&theme=light&" + querystring + "&width=1500&height=350&panelId="
    # print ( "jsonurl" )
    file = 'config.ini'
    config = ConfigParser ( )
    config.read ( file )
    max_concurrent_dl = int ( config [ 'report' ] [ 'parallelthread' ] )
    # print(max_concurrent_dl)
    logger.info ( "using thread %s for downloading the images :" , max_concurrent_dl )

    dl_sem = threading.Semaphore ( max_concurrent_dl )

    downloadloc = "images\\"

    def downloadmutlithread(sourceurl , path , pid) :
        print ( "download {}  {} ".format ( sourceurl , path + str ( pid ) ) )
        logger.info ( "download image %s %s :" , sourceurl , path + str ( pid ) )

        try :
            dl_sem.acquire ( )
            urlretrieve ( sourceurl , downloadloc + path + "_" + str ( pid ) + ".png" , )

        except HTTPError as e :
            print ( e.read ( ) )
            logging.error ( f'{e.read ( )}' )
        finally :

            dl_sem.release ( )

        # urlretrieve ( sourceurl , destination )

    for f in os.listdir ( downloadloc ) :
        os.remove ( os.path.join ( downloadloc , f ) )

    def downloadimage(dictlist) :
        threads=[]

        for k , v in dictlist.items ( ) :
        #    print ( "downloadimage  {} name {} ".format ( k , v ) )

            # path = k
            path = regex.sub ( '' , k )

            if type ( v ) == list :
               # print ( "list" )
                for i in v :
                    pid = i
                    sourceurl = imageurl + str ( pid )
                    destination=downloadloc + path + "_" + str ( pid ) + ".png"
                   # print ( destination )
                  #  urlretrieve ( sourceurl , downloadloc + path + "_" + str ( pid ) + ".png" )

                   # wget.download ( sourceurl , downloadloc + path + "_" + str ( pid ) + ".png" )
            else :
                pid = v
                sourceurl = imageurl + str ( pid )

                destination = downloadloc + path + "_" + str ( pid ) + ".png"
               # print ( destination )
                #urlretrieve ( sourceurl , downloadloc + path + "_" + str ( pid ) + ".png" )
               # wget.download ( sourceurl , downloadloc + path + "_" + str ( pid ) + ".png" )
            #urlretrieve ( sourceurl , downloadloc + path + "_" + str ( pid ) + ".png" )
            t=threading.Thread(target=downloadmutlithread,args=(sourceurl,path,pid))
            t.start()
            threads.append(t)
        for t in threads:
            logger.info ( "Thread details %s" , t )
            t.join ()


    # fetch panel ID from jsonURL :
    with urllib.request.urlopen ( jsonurl ) as url :
        data = json.loads ( url.read ( ).decode ( ) )
        # calling function from parsejson.py
        dict1 = parse_json_recursively ( data , "id" )

    start_time = time.time ( )
    downloadimage ( dict1 )
    duration = time.time ( ) - start_time
    logger.info ( "time taken to download %s  images in  %s in seconds" , len ( dict1 ) , duration )
    print ( f"Downloaded {len ( dict1 )} in {duration} seconds" )
    dict1.clear ( )
    createreport ( downloadloc , file_path , testlist )
    testlist.clear ( )

    for f in os.listdir ( downloadloc ) :
        logger.info ( "deleting the images as the report is generated" )
        os.remove ( os.path.join ( downloadloc , f ) )
