# acquisuite_pipeline
Webserver to accept data push from Obvius Acquisuite

## Purpose 
The goal of this project is to successfully acquire data from Obvius's Data Acquisition System, AcquiSuite.
We take the xml files pushed from the AcquiSuites, filter what we need, and output the data 
to our proprietary database, SkySpark. 

Note that there is an additional Jupyter Notebook that allows data visualization for time deltas in both barchart and histogram
form. Please read comments for additional information. 

## Getting Started
The primary source file to run is webserver.py.
It contains a Flask application that runs a webserver on localhost:8080, 
which is where the AquiSuites will be pushing data to.

### Miscellaneous Issues
This section is to help with identifying problamatic issues within the webserver system. 

#### AcquiSuite PULL/PUSH Response
The AcquiSuite will only delete backlogged files if it receives a properly formatted "SUCCESS" message.
This is important, clearly, since the AcquiSuite can only store so much data and files need to eventually be deleted.
There is an example within webserver.py which gives a correctly labeled XML-style format, but note that there are other 
ways to go about this! I have seen HTML and php style responses as well.

### Prerequisites 
Code runs with Python 3.6 and above.

## Deployment
Project is deployed by running webserver.py through Powershell, cmd, or terminal. 

### Running
```
python webserver.py
```
You should see "Serving Flask app "webserver" (lazy loading)" if the server is running properly.

### Terminating Server
To terminate the server, simply use Ctrl-C.

## Authors
* **Thomas Huo** - *Server/Data acquisition designer* - [Thomas Huo](https://github.com/JinhaoHuo)

## Acknowledgements 

* Chris Weyandt - proposed the project, helped with device-specific hardware issues, and gave feedback
