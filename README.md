# acquisuite_pipeline
Webserver to accept data push from Obvius Acquisuite

## Purpose 
The goal of this project is to successfully acquire data from Obvius's Data Acquisition System, AcquiSuite.
We take the xml files pushed from the AcquiSuites, filter what we need, and output the data 
to our proprietary database, SkySpark. 

## Getting Started
The primary source file to run is webserver.py.
It contains a Flask application that runs a webserver on localhost:8080, 
which is where the AquiSuites will be pushing data to.

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
