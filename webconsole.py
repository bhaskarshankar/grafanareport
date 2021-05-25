import json
import os
import urllib
import time
import pandas as pd
from configparser import ConfigParser
from threading import Thread
from flask_wtf import FlaskForm
import flask
from flask import send_file , jsonify
from flask import Flask , render_template , request
from wtforms import Form , StringField , SelectField
from wtforms.validators import InputRequired
from urllib.parse import urlparse , parse_qs
from main_v1 import *

file = 'config.ini'
config = ConfigParser ( )
config.read ( file )
grafanhost = [ ]
grafanahostc = (config [ 'grafana' ] [ 'host' ])
for i in grafanahostc.split ( ',' ) :
    grafanhost.append ( i )

app = Flask ( __name__ )
# app.config.from_object ( 'config' )
app.config [ 'SECRET_KEY' ] = '7d441f27d441f27567d441f2b6176a'


def fetchdb(grafanahost) :
    jsonurl = "http://" + grafanahost + "/api/search?query=%"
    dbname = [ ]
    with urllib.request.urlopen ( jsonurl ) as url :
        data = json.loads ( url.read ( ).decode ( ) )

    df_nested_list = pd.json_normalize ( data )
    df2 = (df_nested_list [ [ 'uid' , 'uri' , 'type' ] ])  # 1
    print ( df2 )

    for index , row in df2.iterrows ( ) :
        if (row [ 'type' ] == 'dash-db') :
            uri = row [ 'uri' ].split ( '/' )
            uid = row [ 'uid' ]
            print ( "UDI {} ,URI {}" , uid , uri )
            dbname.append ( (uri [ 1 ]) )

    return dbname


@app.route ( '/' , methods=[ 'GET' , 'POST' ] )
def register() :
    error = ""
    form = Form ( )
    testlist = [ ]

    args = request.url
    parsed_url = urlparse ( args )
    dashboardname = str ( parse_qs ( parsed_url.query ) [ 'dashbordname' ][0] )


    if request.method == 'POST' :
        grafanhost = form.grafanhost.data
        dashboardname = dashboardname
        print (  ( dashboardname ) )
        reportname = form.reportname.data
        testlist.append ( ("TestDetails" , form.TestDetails.data) )
        testlist.append ( ("envDetails" , form.envDetails.data) )
        testlist.append ( ("userdetails" , form.userdetails.data) )
        reportname += ".docx"
        args = request.url
        querystring1 = args.split ( sep="&" )
        querystring='&'
        querystring = querystring.join ( querystring1 [ 1 : ] )
        print ( dashboardname )


        print ( querystring )
        start_task ( grafanhost , querystring , reportname , dashboardname , testlist )
        filepart = reportname.split ( "." )
        return render_template ( 'downloads.html' , value=filepart [ 0 ] )

    return render_template ( 'index.html' , form=form , message=error , dashboardname=dashboardname)


@app.route ( '/start_task' )
def start_task(hostname , querystring , reportname , dashboardname , testlist) :
    def inner(reportname) :
        # simulate a long process to watch
        print ( dashboardname )
        file_path = "output\\" + reportname
        time_to_wait = 600
        time_counter = 0
        while not os.path.exists ( file_path ) :
            print ( "Bhaskar_start_filecheck" )
            time.sleep ( 1 )
            time_counter += 1
            if time_counter > time_to_wait : break
        try :
            #  print("Bhaskar_start_task_download")
            #
            print ( "Bhaskar_start_redirect" )
            # return render_template('downloads.html')

        except Exception as e :
            return str ( e )

    def do_work(hostname , querystring , reportname , dashboardname , testlist) :
        print(dashboardname)
        grafanareport ( hostname , querystring , reportname , dashboardname , testlist )
        import time
        time.sleep ( 1 )

    # pythoncom.CoInitialize ( )
    thread = Thread ( target=do_work ( hostname , querystring , reportname , dashboardname , testlist ) ,
                      kwargs={'value' : request.args.get ( 'value' , 20 )} )
    thread.start ( )
    return flask.Response ( inner ( reportname ) , mimetype='text/html' )


@app.route ( '/return_filesdocx/<string:reportname>' , methods=[ 'GET' , 'POST' ] )
def return_filesdocx_tut(reportname) :
    try :
        file_path = "output\\" + reportname
        return send_file ( file_path , attachment_filename=file_path )
    except Exception as e :
        return str ( e )


class Form ( FlaskForm ) :
    grafanhost = SelectField ( 'grafanhost' , choices=grafanhost )
    dashboardname = StringField ( 'dashboardname' , validators=[ InputRequired ( ) ] )
    reportname = StringField ( 'Reportname' , validators=[ InputRequired ( ) ] )
    TestDetails = StringField ( 'TestDetails' , validators=[ InputRequired ( ) ] )
    envDetails =  StringField( 'envDetails',description= "optional  Tets env ,config changes etc ",default="NA",)
    userdetails = StringField ( 'userdetails',description="optional input who executed the test",default="NA" )


@app.route ( '/dbname/<grafanhost>' )
def dbname(grafanhost) :
    dbnames = fetchdb ( grafanhost )
    return jsonify ( {'dbnames' : dbnames} )


if __name__ == '__main__' :
    # app.config.from_object (  )
    reporthost = (config [ 'report' ] [ 'ip' ])
    reportport = (config [ 'report' ] [ 'port' ])
    Debug = (config [ 'report' ] [ 'debug' ])
    app.debug = False
    print ( Debug )
    app.run ( reporthost , reportport )
