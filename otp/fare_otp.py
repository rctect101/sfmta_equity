#!/usr/bin/env python
# coding: utf-8



import requests, json, time
import pandas as pd
import geopandas as gpd
import concurrent.futures
import configparser
import argparse
import datetime
from datetime import timedelta
from subprocess import Popen, call
import subprocess
import sys
import os
import traceback
import csv
import sqlite3

from pathlib import Path
root_path = Path(os.getcwd())
fare_path = str(Path(os.getcwd()).parent) + '/fare'


sys.path.insert(1, str(root_path.parent)+'/fare')
import fare


# shell command to start up otp server
def call_otp():
    
    #graph_path = config[region]['graphs']
    #otp_path = config['General']['otp']
    otp_path = 'C:/Users/ryanm/UCLADrive/205A_Capstone/EquityTool/GitProject/Data/otp'
    graph_path = 'C:/Users/ryanm/UCLADrive/205A_Capstone/EquityTool/GitProject/Data/data/San Francisco-Oakland/otp/graphs'
    date = '2021-12-28'
    
    command = ['java', '-Xmx208G', '-jar', otp_path+'/otp-1.4.0-shaded.jar', '--router', 'graphs-'+date,
          '--graphs', graph_path, '--server', '--enableScriptingWebService']
    
    print('\njava -Xmx4G -jar ' + otp_path+'/otp-1.4.0-shaded.jar'+ ' --router '+ 'graphs-'+date+
          ' --graphs '+graph_path+' --server'+' --enableScriptingWebService\n')
    p = Popen(command)
    
    time.sleep(90) #time needed to ensure the otp server starts up
    return p

def call_otp_otm():
    
    #graph_path = config[region]['graphs']
    #otp_path = config['General']['otp']
    otp_path = 'C:/Users/ryanm/UCLADrive/205A_Capstone/EquityTool/GitProject/Data/otp'
    graph_path = 'C:/Users/ryanm/UCLADrive/205A_Capstone/EquityTool/GitProject/Data/data/San Francisco-Oakland/otp/graphs'
    date = '2021-12-28'
    pointset_path = 'C:/Users/ryanm/UCLADrive/205A_Capstone/EquityTool/GitProject/sfmta_equity/otp/pointsets'
    
    command = ['java', '-Xmx208G', '-jar', otp_path+'/otp-1.4.0-shaded.jar', '--router', 'graphs-'+date,
          '--graphs', graph_path, '--server', '--enableScriptingWebService', '--analyst', '--pointSets', pointset_path]
    
    print('\njava -Xmx4G -jar ' + otp_path+'/otp-1.4.0-shaded.jar'+ ' --router '+ 'graphs-'+date+
          ' --graphs '+graph_path+' --server'+' --enableScriptingWebService\n' + 
           ' --analyst' + ' --pointSets ' + pointset_path + ' ONE TO MANY')
    p = Popen(command)
    
    time.sleep(90) #time needed to ensure the otp server starts up
    return p

# function to return the itineraries
def return_itineraries(param):

    ox = param[0]
    oy = param[1]
    dx = param[2]
    dy = param[3]
    date_us = param[4]
    hr = param[5]
    minute = param[6]

	# parameters
    options = {
   		'fromPlace': str(oy) + ", " + str(ox),
   		'toPlace': str(dy) + ", " + str(dx),
   		'time': str(hr)+':' + str(minute),
   		'date': date_us,
   		'mode': 'TRANSIT,WALK',
   		'maxWalkDistance':5000,
   		'clampInitialWait':0,
   		'wheelchair':False,
   		#'batch': True,
   		'numItineraries': 1
   	}
   
   	# send to server and get data
    response = requests.get(
   		"http://localhost:8080/otp/routers/default/plan",
   		params = options
           )
    # return as json
    #print("JSON is " + json.loads(response.text))
    data = json.loads(response.text)
    return data

def return_itineraries_otm(param):

    ox = param[0]
    oy = param[1]
    date_us = param[2]
    hr = param[3]
    minute = param[4]
    
	# parameters
    surface_options = {
   		'fromPlace': str(oy) + ", " + str(ox),
   		'time': str(hr)+':' + str(minute),
   		'date': date_us,
   		'mode': 'TRANSIT,WALK',
   		'maxWalkDistance':5000,
   		'clampInitialWait':0,
   		'wheelchair':False,
   		'batch': True,
   	}
    
    #create surface
    surf_resp = requests.post(
        "http://localhost:8080/otp/surfaces",
   		params = surface_options)
   
    surf_data = json.loads(surf_resp.text)
    #print(surf_data)

   # parameters
    options = {
   		'targets': 'destinations_01',
   		'detail':'true'
   	}

   	# send to server and get data
    response = requests.get(
   		"http://localhost:8080/otp/surfaces/" + str(surf_data['id']) + "/indicator",
   		params = options)

    data = json.loads(response.text)
    return data


