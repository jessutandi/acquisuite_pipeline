import os
import xml.etree.ElementTree as ET 
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from flask import Flask, flash, request, redirect, url_for

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
#     print(type(request.data))
#     byte_to_string = request.data.decode("utf-8")
#     clean_xml = byte_to_string.replace("\r\n", "")
#     tree = ET.ElementTree(ET.fromstring(clean_xml))
    tree = ET.parse('xmlTest.xml')
    return get_data_xml(tree)

def get_data_xml(xmlTree):
    gbl_tbl = pd.DataFrame(columns=["Record", "Address", "Point", "Name", "Value"])
    root = xmlTree.getroot()
    counter = 1
    address = 0
    string = ""
    for d in root.iter('device'):
        address = d.find('address').text
    
    #This block specifically targets pulses 1 and 8. Not generalized yet!
    #How this works: We changed the XML file to a tree, then iterate through the child nodes with "record" as its tag,
    #Then we find all values and names of the Pulses we want
    #TODO: need to find dateTimes, address, and point values
    for record in root.iter('record'):
        time = record.find('time').text
        for child in record:         
            if "value" in child.attrib:
                string += "RECORD " + str(counter) + " "
                string += child.attrib["name"] + " " + child.attrib["value"] + " "
                tbl = pd.DataFrame(data=[[counter, address, child.attrib['number'], child.attrib['name'], child.attrib['value'], time]], 
                                   columns=["Record", "Address", "Point", "Name", "Value", "Time"])
                gbl_tbl = gbl_tbl.append(tbl, ignore_index=True)
        counter += 1
    gbl_tbl.to_csv('data/' + address + '_data.csv', index=False)
    print(string)
    return string

@app.route('/get_data')#, methods = ['GET', 'POST'])
#get address, point, start, end
#start and end are times, and must be in the format YEAR-MONTH-DAY (ex: 2019-06-17)
#NOTE: the csv files are formated as ADDRESS_data.csv (ex: 250_data.csv)
#NUANCES: start and end must have their hours separated by "_" (ex: 2019-06-17_02:55:00)
def get_data():
    address = request.args.get('address')
    points = request.args.get('points')
    start = request.args.get('start')
    end = request.args.get('end')
    
    #NOTE: in order to bypass Flask list problems, this code takes points as a long string and splits it
    points = points.split(",")
    
    table = pd.read_csv("data/" + address + "_data.csv")
    table = table[table['Point'].isin(points)]
    
    #NOTE: converting start and end to datetimes
    #NOTE: do we need to keep hours? Currently I am, which requires more user input
    start = start.replace("_", " ")
    end = end.replace("_", " ")
    start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    table["Time"] = table["Time"].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

    #Filtering now by time
    table = table[(table['Time'] >= start) & (table['Time'] <= end)]
    
    print(table.to_csv(index=False))
    return table.to_csv(index=False)
    #EXAMPLE URL: http://localhost:8080/get_data?address=250&points=1,2,3&start=2019-06-17_02:55:00&end=2019-06-17_03:05:00

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
    
    
    
    
    
    
    
    
    