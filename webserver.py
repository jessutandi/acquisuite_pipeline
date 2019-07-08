import os
import xml.etree.ElementTree as ET 
import pandas as pd
import numpy as np
from pathlib import Path
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

# # @app.route('/get_data', methods = ['GET', 'POST'])
# # this is getting info from the args, and return the respective dataframe
# def get_data(address, point, start=0, end=0):
#     tbl = gbl_tbl[(gbl_tbl['Address'] == address) & (gbl_tbl['Point'] == point)]
#     return tbl.to_html(header="true", table_id="table")
#     #TODO: make index by address or record?
    
# # use this function in get_data_xml to push data to a dataframe
# #TODO: Find a way to make this not take repeat data
# def push_data(record, address, point, name, value):
#     tbl = pd.DataFrame(data=[[record, address, point, name, value]], columns=["Record", "Address", "Point", "Name", "Value"])
#     gbl_tbl = gbl_tbl.append(tbl, ignore_index=True)

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
        for child in record:
            if "value" in child.attrib:
                if child.attrib["name"] == "Pulse_1" or child.attrib["name"] == "Pulse_8":
                    string += "RECORD " + str(counter) + " "
                    string += child.attrib["name"] + " " + child.attrib["value"] + " "
                    #push_data(counter, address, child.attrib['number'], child.attrib['name'], child.attrib['value'])
                    tbl = pd.DataFrame(data=[[counter, address, child.attrib['number'], child.attrib['name'], child.attrib['value']]], 
                                       columns=["Record", "Address", "Point", "Name", "Value"])
                    gbl_tbl = gbl_tbl.append(tbl, ignore_index=True)
        counter += 1
    gbl_tbl.to_csv('record_data', index=False)
    print(string)
    return string

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
    
    
    
    
    
    
    
    
    