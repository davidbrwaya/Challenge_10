# Import the necessary libraries
import numpy as np
import pandas as pd
from datetime import datetime

from flask import Flask, jsonify, abort

# SQLAlchemy dependencies
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################

# Create the database engine
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create a Flask application
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define a custom error handler for invalid date format
@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

# Define a custom error handler for start date after end date
@app.errorhandler(400)
def handle_start_after_end_error(error):
    return jsonify({"error": "Start date must occur before end date."}), 400

# Define the route to get temperature data from a given start date
@app.route("/api/v1.0/<start>")
def start_temp_data(start):
    """Return the minimum, average, and maximum temperatures from a given start date."""
    try:
        start_date_dt = datetime.strptime(start, "%Y-%m-%d").date()
    except ValueError:
        abort(400)

    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    range_data = session.query(*sel).filter(Measurement.date >= start_date_dt).all()

    data_dict = {
        'min_temp': range_data[0][0],
        'max_temp': range_data[0][1],
        'avg_temp': round(range_data[0][2], 2)
    }

    return jsonify(data_dict)

# Define the route to get temperature data from a given start and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end_temp_data(start, end):
    """Return the minimum, average, and maximum temperatures from given start and end dates."""
    try:
        start_date_dt = datetime.strptime(start, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        abort(400)

    if start_date_dt > end_date_dt:
        abort(400)

    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    range_data = session.query(*sel).filter(Measurement.date >= start_date_dt, Measurement.date <= end_date_dt).all()

    data_dict = {
        'min_temp': range_data[0][0],
        'max_temp': range_data[0][1],
        'avg_temp': round(range_data[0][2], 2)
    }

    return jsonify(data_dict)

# Run the application if executed as the main script
if __name__ == '__main__':
    app.run(debug=True)