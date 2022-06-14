# Database Setup
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


# Flask Setup

app = Flask(__name__)

# Flask Routes


@app.route("/")
def homepage():
    return(
        f'Welcome to Honolulu, Hawaii climate analysis API! <br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/temp/start/end'
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.


@app.route("/api/v1.0/precipitation")
def prcp():

    # Query the date and precipitation
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipipation = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= start_date).all()

    session.close()

    # Convert to dictionary with date as key and prcp as value
    precip = {date: prcp for date, prcp in precipipation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return the list of stations"""
    station = session.query(Station.station).all()

    session.close()
    station_list = list(np.ravel(station))
    return jsonify(station_list=station_list)


@app.route("/api/v1.0/tobs")
def temp():
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station_temp = session.query(Measurement.tobs).filter(
        Measurement.date >= start_date).filter(Measurement.station == "USC00519281").all()
    session.close()
    temp_list = list(np.ravel(active_station_temp))
    return jsonify(temp_list=temp_list)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return maximum, average and minimum temperature"""
    sel = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        temp_results = session.query(
            *sel).filter(Measurement.date >= start_date).all()

        session.close()

        temps = list(np.ravel(temp_results))
        return jsonify(temps)

    start_date = dt.datetime.strptime(start, "%m%d%Y")
    end_date = dt.datetime.strptime(end, "%m%d%Y")
    temp_results = session.query(
        *sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    temps = list(np.ravel(temp_results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()
