import os
import xml.etree.ElementTree as ET 
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from flask import Flask, flash, request, redirect, url_for, make_response, jsonify

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

    resp = make_response("<?xml version=\"1.0\"?>\n<DAS>\n<result>SUCCESS</result>\n</DAS>\n")
    resp.headers['Status'] = '200 OK'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Content-Type'] = 'text/xml'
    return resp

def get_data_xml(xmlTree):
    gbl_tbl = pd.DataFrame(columns=["Record", "Address", "Point", "Name", "Value"])
    root = xmlTree.getroot()
    address = 0
    for d in root.iter('device'):
        address = d.find('address').text

    #How this works: We changed the XML file to a tree, then iterate through the child nodes with "record" as its tag,
    for record in root.iter('record'):
        time = record.find('time').text
        for child in record:         
            if "value" in child.attrib:                 
                tbl = pd.DataFrame(data=[[address, child.attrib['number'], 
                                          child.attrib['name'], child.attrib['value'],time]], 
                                   columns=["Address", "Point", "Name", "Value", "Time"])
                gbl_tbl = gbl_tbl.append(tbl, ignore_index=True)
                #checking for duplicates
                if os.path.isfile('data/' + address + '_data.csv'):
                    existing = pd.read_csv('data/' + address + '_data.csv')
                    existing = existing.append(gbl_tbl)
                    existing = existing[~existing.duplicated()]
                    gbl_tbl = existing
    gbl_tbl.to_csv('data/' + address + '_data.csv', index=False)
    return ''

@app.route('/get_data')
#start and end are times, and must be in the format YEAR-MONTH-DAY (ex: 2019-06-17)
#NOTE: the csv files are formated as ADDRESS_data.csv (ex: 250_data.csv)
#NUANCES: start and end must have their hour and smaller units separated by "_" (ex: 2019-06-17_02:55:00)
def get_data():
    address = request.args.get('address')
    pulses = request.args.get('pulses')
    start = request.args.get('start')
    end = request.args.get('end')
    
    #NOTE: in order to bypass Flask list problems, this code takes points as a long string and splits it
    #We also created a regex string to filter the table for our required points
    #Please black box this section, some of the symbols are needed for regex
    pulses = pulses.split(",")
    regexed = "_" + pulses[0]
    for pulse in pulses:
        regexed += "|_" + pulse
    
    table = pd.read_csv("data/" + address + "_data.csv")
    table = table[table['Name'].str.contains(regexed)]
    
    #NOTE: converting start and end to datetimes
    start = start.replace("_", " ")
    end = end.replace("_", " ")
    start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    table["Time"] = table["Time"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

    #Filtering now by time
    table = table[(table['Time'] >= start) & (table['Time'] <= end)]
    
    #Dropping NaN values in Value column
    table = table.dropna(subset=['Value'])
    
    print(table.to_csv(index=False))
    #return table.to_csv(index=False)
    return table.to_html(header="true", table_id="table")
    #EXAMPLE URL: http://localhost:8080/get_data?address=250&pulses=1,2,3&start=2019-07-15_02:05:00&end=2019-07-15_02:15:00

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
    
    
    
    
    
    
    
    
    