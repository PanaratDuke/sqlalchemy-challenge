import numpy as np
import pandas as pd
import datetime as dt
from flask import jsonify, Flask
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import (Column, Date, Integer, MetaData, Table, Text, create_engine, func, inspect,select)

engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

#--Create classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from Python to the DB
# session = Session(engine)
app = Flask(__name__)
#--------------------------
# app.route(rule, options)  
# It accepts the following parameters.

# rule: It represents the URL binding with the function.
# options: It represents the list of parameters to be associated with the rule object
#---------------------------
@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"Welcome to SQLAlchemy Homework<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tempInfo/<start_date>/<end_date><br/>"
        f"/api/v1.0/tempInfo/<start_date><br/>"
        f"/api/v1.0/tempInfo<br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using 'date' as the key and 'prcp' as the value"""

    # # Create session from Python to the DB
    session = Session(engine)
    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)   
    # Query precipitation
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    preciptations = []

    for result in results:
        prcp_dict = {}
        prcp_dict["date"] = result[0]
        prcp_dict["prcp"] = result[1]
        preciptations.append(prcp_dict)

    
    return jsonify(preciptations)
    
    session.close()

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    # Most active stations query using .count() to find station that has the most count and sorted
    stations_results = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\
                .order_by(func.count(Measurement.station).desc()).all()
    # With np.ravel will showed 1-D list otherwise it'll show list in the list
    stations_results = list(np.ravel(stations_results))
    
    session.close()
    return jsonify(stations_results)

@app.route("/api/v1.0/tobs")
def tobs():
    """A List of temperature observation (TOBS) for the previous year 
    from the most active station."""
    session = Session(engine)

    # Set Most Active Station in the variable
    most_active = session.query(Measurement.station, func.count(Measurement.station))\
                .group_by(Measurement.station)\
                .order_by(func.count(Measurement.station).desc())\
                .first()[0]
    
    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prev_year
    
    # Perform a query to retrieve the data and precipitation scores
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prev_year)\
                .filter(Measurement.station == f"{most_active}").all()

    session.close()
    return jsonify(tobs_results)

@app.route("/api/v1.0/tempInfo/<start_date>/<end_date>")
@app.route("/api/v1.0/tempInfo/<start_date>")
@app.route("/api/v1.0/tempInfo")
def get_info(start_date=None,end_date=None):
    """
    /api/v1.0/tempInfo/<start_date>/<end_date> with two arguments will return 
    average, min and max temperatures from start date to end date.
    /api/v1.0/tempInfo/<start_date> with on arguments will return
    average, min and max temperatures from start date until present.
    """
    session = Session(engine)
    
    if start_date is None and end_date is None:
        return (f"Input Start Date and End Date using this format YYYY-MM-DD")

    elif start_date is not None and end_date is None:
        start_temp_details = session.query(func.min(Measurement.tobs)\
                 ,func.avg(Measurement.tobs)\
                 ,func.max(Measurement.tobs))\
                .filter(Measurement.date >= start_date).all()

        start_temp_details_unravel = list(np.ravel(start_temp_details))

        start_temp_detail_dict = {
                        "Minimum Temperature":start_temp_details_unravel[0],
                        "Average Temperature":start_temp_details_unravel[1],
                        "Maximum Temperature":start_temp_details_unravel[2]
                        }
        return (start_temp_detail_dict)

    else:
        temp_details = session.query(func.min(Measurement.tobs)\
                 ,func.avg(Measurement.tobs)\
                 ,func.max(Measurement.tobs))\
                .filter(Measurement.date >= start_date)\
                .filter(Measurement.date <= end_date).all()

        temp_unravel = list(np.ravel(temp_details))
# f"Temperature Info between {start_date} and {end_date}"
        temp_detail_dict = {
                        "Minimum Temperature":temp_unravel[0],
                        "Average Temperature":temp_unravel[1],
                        "Maximum Temperature":temp_unravel[2]
                        }
    session.close()
    return jsonify(temp_detail_dict)
    



#--------------------------------------
# Finally, the run method of the Flask class is used to run the flask application on the local development server.
# The syntax is given below.
# *****  app.run(host, port, debug, options)  
# SN	Option	Description
# 1	host	The default hostname is 127.0.0.1, i.e. localhost.
# 2	port	The port number to which the server is listening to. The default port number is 5000.
# 3	debug	The default is false. It provides debug information if it is set to true.
# 4	options	It contains the information to be forwarded to the server.
#----------------------------------------

#print(f"Hi My Name is {__name__}") : This will generate "Hi My Name is app" which
#is not match with "__main__" which generated by Python, therefore web browser won't run



if __name__ == "__main__":
    app.run(debug=True) 