import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def Home_page():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;/&gt;end&lt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all prcp
    dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    dates # datetime.date(2016, 8, 23)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, func.avg(Measurement.prcp)).\
            filter(Measurement.date.between (dates, dt.date(2017, 8, 23))).group_by('date')
    session.close()
    
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    session = Session(engine)
    #     """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all stations
    results = session.query(Station.name).dictinct
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Return a JSON list of stations from the dataset.
    session = Session(engine)
    dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    dates # datetime.date(2016, 8, 23)
    #     """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all stations
    results = session.query(Measurement.date, Measurement.tobs)\
                .filter(Measurement.station == USC00519281, Measurement.date.between(dates, dt.date(2017, 8, 23)))\
                .group_by(Measurement.date)\
                .order_by(Measurement.date)
    session.close()
    temp_obser_12 = list(np.ravel(results))
    return jsonify(temp_obser_12)


if __name__ == '__main__':
    app.run(debug=True)
