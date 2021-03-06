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
        f"Available Routes:<br>"
        f"==================================================<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;date&gt; (replace &lt;date&gt; with date in yyyy-mm-dd format)<br>"
        f"/api/v1.0/&lt;date&gt;/&lt;date&gt; (replace &lt;date&gt;/&lt;date&gt; with date in yyyy-mm-dd/yyyy-mm-dd format)<br>"
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
    results = session.query(Station.station, Station.name).all()
    session.close()
    Station_list = list(results) #list(np.ravel(results))
#     Station_list = []
#     for stat in results:
#         Station_list.append(stat)
    
    return jsonify(Station_list)

@app.route("/api/v1.0/tobs")
# Return a JSON list of temperature observations (TOBS) for the previous year
def tobs():
    session = Session(engine)
    dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    dates # datetime.date(2016, 8, 23)
    # Query all stations
    results = session.query(Measurement.date, Measurement.tobs)\
                .filter(Measurement.station == 'USC00519281', Measurement.date.between(dates, dt.date(2017, 8, 23)))\
                .group_by(Measurement.date)\
                .order_by(Measurement.date)
    session.close()
#     temp_obser_12 = list(np.ravel(results))
    tobs_list = []
    for tob in results:
        tobs_list.append(tob)
    return jsonify(tobs_list)

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# Start Day Route
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    range_list = []
    if len(start_date) == 10:
        session = Session(engine)
        range_calc = session.query(Measurement.date.label("Date"), func.min(Measurement.tobs).label("Min"),\
                               func.avg(Measurement.tobs).label("Avg"), func.max(Measurement.tobs).label("Max")).\
        filter(Measurement.date >= start_date).\
        group_by(Measurement.date).all()
        session.close()
        for r in range_calc:
            range_list.append(f'date: {r.Date} Min temperature:{r.Min} Avg temperature:{round(r.Avg,2)}, Max temperature: {r.Max}')       
    else:
        range_list.append(f'Incorrect date {start_date} format, should be YYYY-MM-DD')
    return jsonify(range_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def range(start_date,end_date):
    range_list = []
    if len(start_date) == 10 and len(end_date) == 10:
        session = Session(engine)
        range_calc = session.query(Measurement.date.label("Date"), func.min(Measurement.tobs).label("Min"),\
                                   func.avg(Measurement.tobs).label("Avg"), func.max(Measurement.tobs).label("Max")).\
        filter(Measurement.date.between(start_date,end_date)).\
        group_by(Measurement.date).all()
        session.close()
        # Convert List of Tuples Into Normal List
    #     range_list = list(range_calc)
    #     for date in range_calc:
        for r in range_calc:
            range_list.append(f'date: {r.Date} Min temperature:{r.Min} Avg temperature:{round(r.Avg,2)}, Max temperature: {r.Max}')
    else:
        range_list.append(f'Incorrect date {start_date}/{end_date} format, should be YYYY-MM-DD/YYYY-MM-DD')
    # Return JSON List calculate `TMIN`, `TAVG`, and `TMAX` range
    return jsonify(range_list)

if __name__ == '__main__':
    app.run(debug=True)
