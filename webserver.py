import os
import xml.etree.ElementTree as ET 
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from datetime import datetime
from flask import Flask, flash, request, redirect, url_for, make_response

#BIG NOTE: PLEASE TURN OFF FIREWALL TO HAVE ACQUISUITE WORK! Need to figure out a protocol to allow AcquiSuite. 
                  
app = Flask(__name__)
app.secret_key = "super secret"
@app.route('/', methods = ['GET', 'POST'])
def default():
    print("--Entering default()--")
    print("HEADERS: ", request.headers)
    print("REQ_PATH: ", request.path)
    print("ARGS: ", request.args)
    print("DATA: ", request.data)
    print("FORM: ", request.form)
    
    #This block takes the request.data, which is encoded in bytes, and decodes it to a string and cleans it. We then make it an XML tree.
    try: 
        byte_to_string = request.data.decode("utf-8")
        clean_xml = byte_to_string.replace("\r\n", "")
        tree = ET.ElementTree(ET.fromstring(clean_xml))
        get_data_xml(tree)
    except:
        print('SUCCESS START UP')

    #This section is important in response to the AcquiSuite response. This XML response is the only way to 
    #properly respond to the AcquiSuite in which it will receive a "SUCCESS" indicator and delete backlogged files.
    #This works by sending a properly formatted XML string with HTML style headers. The biggest issue was that 
    #Content-Type is defaulted to text/html for the AcquiSuite, so that needed to be changed. 
    resp = make_response("<?xml version=\"1.0\"?>\n<DAS>\n<result>SUCCESS</result>\n</DAS>\n")
    resp.headers['Status'] = '200 OK'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Content-Type'] = 'text/xml'
    return resp

#TODO: Need to separate csv files by Point rather than Address
def get_data_xml(xmlTree):
    #Initialization of DataFrame
    gbl_tbl = pd.DataFrame(columns=["Address", "Point", "Name", "Value", "Time"])
    
    #Getting the root of the xmlTree and initializing address
    root = xmlTree.getroot()
    address = 0
    for d in root.iter('device'):
        address = d.find('address').text

    #How this works: We changed the XML file to a tree, then iterate through the child nodes with "record" as its tag
    for record in root.iter('record'):
        #Get the time of the record entry
        time = record.find('time').text
        #Iterate through all points within the record
        for child in record:
            #This is mainly to get the points, we can alter to specify other info like error messages
            if "value" in child.attrib:
                #Create a DataFrame with line of data (which is really a row right now) to append to main DataFrame
                tbl = pd.DataFrame(data=[[address, child.attrib['number'], 
                                          child.attrib['name'], child.attrib['value'],time]], 
                                   columns=["Address", "Point", "Name", "Value", "Time"])
                #Appending to gbl_tbl
                gbl_tbl = gbl_tbl.append(tbl, ignore_index=True)
                #Checking for duplicates within the file and removing them if found
                if os.path.isfile('data/' + address + '_data.csv'):
                    existing = pd.read_csv('data/' + address + '_data.csv')
                    existing = existing.append(gbl_tbl)
                    existing = existing[~existing.duplicated()]
                    gbl_tbl = existing
                    
    #Converts the DataFrame into a csv file
    gbl_tbl.to_csv('data/' + address + '_data.csv', index=False)
    return 'SUCCESS'

@app.route('/get_data')
#start and end are times, and must be in the format YEAR-MONTH-DAY (ex: 2019-06-17)
#NOTE: the csv files are formated as ADDRESS_data.csv (ex: 250_data.csv)
#NUANCES: start and end must have their hour and smaller units separated by "_" (ex: 2019-06-17_02:55:00)
def get_data():

    #Opens our config file, currently in yaml format
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
    
    #Assigns config values to variables
    address = config['address']
    points = config['points']
    start = config['start']
    end = config['end']
    
    #Starts reading and sorting our table
    table = pd.read_csv("data/" + str(address) + "_data.csv")
    table = table[table['Point'].isin(points)]

    #Changes user string input for start/end to datetime format
    start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    
    #Applies datetime conversion to time column in DataFrame
    table["Time"] = table["Time"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

    #Filtering now by time
    table = table[(table['Time'] >= start) & (table['Time'] <= end)]
    
    #Dropping NaN values in Value column
    table = table.dropna(subset=['Value'])
    
    #Currently returns an html table to the webserver, will eventually need to configure to SkySpark
    return table.to_html(header="true", table_id="table")

    #EXAMPLE URL: http://localhost:8080/get_data?address=250&pulses=1,2,3&start=2019-07-15_02:05:00&end=2019-07-15_02:15:00

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
    
    
    
    
    
    
    
    
    