# Importing necessary libraries and modules
from flask import Flask, request
import stabel_FP
import Scale_factor
import datetime
import requests
from flask import Flask, request, jsonify
import tkinter as tk
import psycopg2
import CDF
import Evaluation
from threading import Thread
import upload_keys
from Design import Design_Check
import Delete_fp
import pandas as pd


# creating a list of multiples of 50 in the range starting from 100 and ending at 250. Also providing a comment describing what the range represents
MaxParticlesM = list(range(100, 251, 50))
minParticlesM = list(range(50, 201, 50))
distSTDM = list(range(3, 10, 2))
bleRSSIcutOffM = [-95, -200]

app = Flask(__name__)


@app.route("/rows_venues", methods=["POST", "GET"])
def rows_venues():
    data = request.json  # assuming the values are sent in JSON format
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))

    conn = psycopg2.connect(
        user=DB_User,           # Username for PostgreSQL
        password=DB_PW,         # Password for PostgreSQL
        host=DB_IP,             # Host IP address of PostgreSQL server
        port=DB_port,           # Port number of PostgreSQL server
        database=DB_name        # Name of the database to connect to
    )

    # why i send data like this [(2, '5.08 Offices'), (3, '5.08 Residential'), and get this like this [[2,"5.08 Offices"],[3,"5.08 Residential"]]
    # This comment is a reminder or a question about why the data is being sent in a specific format and received in a different format.

    # Create a Cursor object
    cursor = conn.cursor()

    query = "SELECT id , venue_name FROM penguin.tblvenues"

    # Execute the query and fetch all rows returned
    cursor.execute(query)
    rows = cursor.fetchall()
    rows_venues = [tuple(sublist) for sublist in rows]

    return rows_venues


@app.route("/rows_venues_0", methods=["POST", "GET"])
def rows_venues_0():
    data = request.json  # assuming the values are sent in JSON format
    venue_name = str(data.get(('venue_name')))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))
    conn = psycopg2.connect(
        user=DB_User,           # Username for PostgreSQL
        password=DB_PW,         # Password for PostgreSQL
        host=DB_IP,             # Host IP address of PostgreSQL server
        port=DB_port,           # Port number of PostgreSQL server
        database=DB_name        # Name of the database to connect to
    )

    # why i send data like this [(2, '5.08 Offices'), (3, '5.08 Residential'), and get this like this [[2,"5.08 Offices"],[3,"5.08 Residential"]]
    # This comment is a reminder or a question about why the data is being sent in a specific format and received in a different format.

    # Create a Cursor object
    cursor = conn.cursor()
    query = f"SELECT id,venue_name FROM penguin.tblvenues WHERE venue_name = '{venue_name}'"

    # Execute the query and fetch all rows returned
    cursor.execute(query)
    rows = cursor.fetchall()
    rows_venues_0 = [tuple(sublist) for sublist in rows]

    return rows_venues_0

@app.route("/rows_floors", methods=["POST", "GET"])
def rows_floors():
    data = request.json  # assuming the values are sent in JSON format
    venue_id = int(data.get(('venue_id')))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))
    conn = psycopg2.connect(
        user=DB_User,           # Username for postgresql
        password=DB_PW,         # Password for postgresql
        host=DB_IP,             # Host IP address of postgresql server
        port=DB_port,           # Port number of postgresql server
        database=DB_name        # Name of the database to connect to
    )

    # Create a Cursor object
    cursor = conn.cursor()
    query = f"SELECT id, floor_name FROM penguin.tblfloors WHERE venue_id={venue_id} AND update_status != 2"

    # Execute the query and fetch all rows returned
    cursor.execute(query)
    rows = cursor.fetchall()
    rows_floors = [tuple(sublist) for sublist in rows]
    return rows_floors


@app.route("/D_O", methods=["POST", "GET"])
def result():
    # Creating lists of different values
    # meters  # creating a list of multiples of 50 in the range starting from 100 and ending at 250. Also providing a comment describing what the range represents
    response_data = {}
    data = request.json  # assuming the values are sent in JSON format

    # Retrieving required data from the request JSON
    venue_id = int(data.get(('venue_id')))
    floor_id = int(data.get('floor_id'))
    montecarloIter = int(data.get('montecarloIter'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))
    PE_Url = str(data.get(('PE_Url')))

    # full URL wit the Database name
    url = PE_Url + f'PEService.svc/Initialize?DbName={DB_name}'
    root = tk.Tk()  # creating a graphical interface
    root.title("CDF")  # Setting the title of the window

    # Getting scaling factor based on venue and floor IDs
    scale_factor = Scale_factor.get_scale_factor(
        floor_id=floor_id, venue_id=venue_id, DB_IP=DB_IP, DB_User=DB_User, DB_PW=DB_PW, DB_name=DB_name, DB_port=DB_port)

    def thread_function_fp():
        global fp_result
        global sig_result
        fp_result = Evaluation.perform_density_analysis_fp(
            venue_id, floor_id, scale_factor, DB_IP, DB_User, DB_PW, DB_name, DB_port)
        sig_result = Evaluation.perform_density_analysis_sig(
            venue_id, floor_id, scale_factor, DB_IP, DB_User, DB_PW, DB_name, DB_port)

    thread_fp = Thread(target=thread_function_fp)

    thread_fp.start()

    thread_fp.join()
# Check if sig_result is None and fp_result is not None
    if sig_result is None and fp_result is not None:
        response_data['response'] = {
            'map_url_fp': fp_result[0],
            'data_sensors_fp': fp_result[1].tolist(),
            'probPoints_fp': fp_result[2].tolist(),
            'linesToBeRepeated_fp': fp_result[3].tolist(),
            'stop_fp': fp_result[4],
            'map_url_sig': [],
            'data_sensors_sig': None,
            'probPoints_sig': None,
            'linesToBeRepeated_sig': None,
            'stop_sig': None
        }

    # Check if fp_result is None and sig_result is not None
    if fp_result is None and sig_result is not None:
        response_data['response'] = {
            'map_url_fp': [],
            'data_sensors_fp': None,
            'probPoints_fp': None,
            'linesToBeRepeated_fp': None,
            'stop_fp': None,
            'map_url_sig': sig_result[0],
            'data_sensors_sig': sig_result[1].tolist(),
            'probPoints_sig': sig_result[2].tolist(),
            'linesToBeRepeated_sig': sig_result[3].tolist(),
            'stop_sig': sig_result[4]
        }

    # Check if fp_result is None and sig_result is None
    if fp_result is None and sig_result is None:
        response_data['response'] = {
            'map_url_fp': [],
            'data_sensors_fp': None,
            'probPoints_fp': None,
            'linesToBeRepeated_fp': None,
            'stop_fp': None,
            'map_url_sig': [],
            'data_sensors_sig': None,
            'probPoints_sig': None,
            'linesToBeRepeated_sig': None,
            'stop_sig': None
        }

    # Check if fp_result and sig_result are not None
    if fp_result != None and sig_result != None:
        response_data['response'] = {
            'map_url_fp': fp_result[0],
            'data_sensors_fp': fp_result[1].tolist(),
            'probPoints_fp': fp_result[2].tolist(),
            'linesToBeRepeated_fp': fp_result[3].tolist(),
            'stop_fp': fp_result[4],
            'map_url_sig': sig_result[0],
            'data_sensors_sig': sig_result[1].tolist(),
            'probPoints_sig': sig_result[2].tolist(),
            'linesToBeRepeated_sig': sig_result[3].tolist(),
            'stop_sig': sig_result[4]
        }

    # Return the response data as JSON
    return jsonify(response_data)


# Route for "/CDF" with methods POST and GET
@app.route("/CDF", methods=["POST", "GET"])
def draw():
    data = request.json  # assuming the values are sent in JSON format

    venue_id = int(data.get(('venue_id')))
    floor_id = int(data.get('floor_id'))
    montecarloIter = int(data.get('montecarloIter'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))
    PE_Url = str(data.get(('PE_Url')))
    Response = str(data.get(('Response')))
    url = PE_Url+f'PEService.svc/Initialize?DbName={DB_name}'

    if Response == 'Yes':
        scale_factor = Scale_factor.get_scale_factor(
            floor_id=floor_id, venue_id=venue_id, DB_IP=DB_IP, DB_User=DB_User, DB_PW=DB_PW, DB_name=DB_name, DB_port=DB_port)

        stabel_FP.convert(venue_id=venue_id, floor_id=floor_id,
                          DB_IP=DB_IP, DB_User=DB_User, DB_PW=DB_PW, DB_name=DB_name, DB_port=DB_port)

        response = requests.request("GET", url)

        start = datetime.datetime.now()
        DiffAll, max_error_D, value, min_sum_key, x_values, y_values = CDF.final(venue_id, floor_id, montecarloIter, scale_factor,
                                                                                 MaxParticlesM, minParticlesM, distSTDM, bleRSSIcutOffM, DB_IP=DB_IP, DB_User=DB_User, DB_PW=DB_PW, DB_name=DB_name, PE_Url=PE_Url, DB_port=DB_port)

        end2 = datetime.datetime.now()
        end_2 = end2 - start
        print(end_2)
        global df_x_y_e
        # Creating a DataFrame with x_values, y_values, and error_values
        df_x_y_e = pd.DataFrame(
            {'x_values': x_values, 'y_values': y_values, 'error_values': DiffAll})

        # Creating a dictionary to store the computed values
        response_data = {}
        response_data['response'] = {
            'DiffAll': DiffAll.tolist(),
            'min_sum_key': min_sum_key,
            'max_error_D': max_error_D,
            'value_at_95th_percentile': value['value_at_95th_percentile']
        }

        # Resetting venue_id and floor_id to None
        venue_id = None
        floor_id = None

        # Returning the computed values as JSON response
        return jsonify(response_data)


@app.route("/Check_Fp", methods=["POST", "GET"])
def Check_Fp():
    data = request.json  # assuming the values are sent in JSON format
    venue_id = int(data.get(('venue_id')))
    floor_id = int(data.get('floor_id'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))

    conn = psycopg2.connect(
        user=DB_User,           # Username for postgresql
        password=DB_PW,         # Password for postgresql
        host=DB_IP,             # Host IP address of postgresql server
        port=DB_port,            # Port number of postgresql server
        database=DB_name        # Name of the database to connect to
    )

    # Create a Cursor object
    cursor = conn.cursor()

    # Execute the query and fetch all rows returned
    cursor.execute("SELECT COUNT(*)  FROM penguin.tblfp_data WHERE venue_id = %s AND floor_id = %s",
                   (venue_id, floor_id))
    Check_Fp = cursor.fetchall()
    return Check_Fp


@app.route("/Check_Fp_sensors", methods=["POST", "GET"])
def Check_Fp_sensors():
    data = request.json  # assuming the values are sent in JSON format
    venue_id = int(data.get(('venue_id')))
    floor_id = int(data.get('floor_id'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))

    conn = psycopg2.connect(
        user=DB_User,           # Username for postgresql
        password=DB_PW,         # Password for postgresql
        host=DB_IP,             # Host IP address of postgresql server
        port=DB_port,            # Port number of postgresql server
        database=DB_name        # Name of the database to connect to
    )

    # Create a Cursor object
    cursor = conn.cursor()

    # Execute the query and fetch all rows returned
    cursor.execute("SELECT COUNT(*)  FROM penguin.tblfp_sensors_data WHERE venue_id = %s AND floor_id = %s",
                   (venue_id, floor_id))
    Check_Fp_sensors = cursor.fetchall()
    return Check_Fp_sensors


@app.route("/Check_Sig", methods=["POST", "GET"])
def Check_Sig():
    data = request.json  # assuming the values are sent in JSON format
    venue_id = int(data.get(('venue_id')))
    floor_id = int(data.get('floor_id'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))

    conn = psycopg2.connect(
        user=DB_User,           # Username for postgresql
        password=DB_PW,         # Password for postgresql
        host=DB_IP,             # Host IP address of postgresql server
        port=DB_port,            # Port number of postgresql server
        database=DB_name        # Name of the database to connect to
    )

    # Create a Cursor object
    cursor = conn.cursor()

    # Execute the query and fetch all rows returned
    cursor.execute("SELECT COUNT(*)  FROM penguin.tblsignature_data WHERE venue_id = %s AND floor_id = %s",
                   (venue_id, floor_id))
    Check_Sig = cursor.fetchall()
    return Check_Sig


@app.route("/Check_Sig_sensors", methods=["POST", "GET"])
def Check_Sig_sensors():
    data = request.json  # assuming the values are sent in JSON format
    venue_id = int(data.get(('venue_id')))
    floor_id = int(data.get('floor_id'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))

    conn = psycopg2.connect(
        user=DB_User,           # Username for postgresql
        password=DB_PW,         # Password for postgresql
        host=DB_IP,             # Host IP address of postgresql server
        port=DB_port,            # Port number of postgresql server
        database=DB_name        # Name of the database to connect to
    )

    # Create a Cursor object
    cursor = conn.cursor()

# The following code connects to a database and performs various operations based on the HTTP methods received.
# It is written in Python programming language.

# This function executes an SQL query to fetch the count of records from the table 'penguin.tblsignature_sensors_data' with specified conditions.
# It takes venue_id and floor_id as parameters.

    cursor.execute("SELECT COUNT(*) FROM penguin.tblsignature_sensors_data WHERE venue_id = %s AND floor_id = %s",
                (venue_id, floor_id))
    Check_Sig_sensors = cursor.fetchall()
    return Check_Sig_sensors

@app.route("/Upload_Keys", methods=["POST", "GET"])
def uploade():
    # Assuming the values are sent in JSON format,
    # this function receives data in JSON and extracts necessary information.
    # It performs an operation based on the value of 'Response' received.

    data = request.json
    floor_id = int(data.get('floor_id'))
    diff_min = data.get('diff_min')
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    PE_Url = str(data.get(('PE_Url')))
    DB_port = str(data.get(('DB_port')))
    Response = str(data.get(('Response')))
    
    url = PE_Url + f'PEService.svc/Initialize?DbName={DB_name}'
    
    if Response == 'Yes':
        # Calls the 'insert_min_key' function passing necessary arguments.
        upload_keys.insert_min_key(DB_IP, DB_User, DB_PW, DB_name, diff_min, floor_id, DB_port)
        

@app.route("/Delete_FP", methods=["POST", "GET"])
def Delete_FP():
    # Similar to previous route, this function receives data in JSON and extracts necessary information.
    # It calls the 'Delete_FP' function passing necessary arguments.

    data = request.json
    floor_id = int(data.get('floor_id'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))
    
    Delete_fp.Delete_FP(floor_id, DB_IP, DB_User, DB_PW, DB_name, DB_port)
        

@app.route("/Design", methods=["POST", "GET"])
def Design():
    # This function receives data in JSON and extracts necessary information.
    # It then calls multiple functions passing the extracted arguments.
    # Finally, it returns a dictionary containing the results of the called functions.
    
    data = request.json
    response_data = {}
    venue_id = int(data.get(('venue_id')))
    floor_id = int(data.get('floor_id'))
    DB_name = str(data.get(('DB_name')))
    DB_User = str(data.get(('DB_User')))
    DB_PW = str(data.get(('DB_PW')))
    DB_IP = str(data.get(('DB_IP')))
    DB_port = str(data.get(('DB_port')))
    ninety_five_percent_error = int(data.get(('ninety_five_percent_error')))
    
    # Calls the 'get_scale_factor' function passing necessary arguments.
    scale_factor = Scale_factor.get_scale_factor(floor_id=floor_id, venue_id=venue_id, DB_IP=DB_IP,
                                                DB_User=DB_User, DB_PW=DB_PW, DB_name=DB_name, DB_port=DB_port)
    
    # Calls the 'Design_Check' function passing necessary arguments.
    Design_Check_1 = Design_Check(venue_id, floor_id, scale_factor, DB_IP, DB_User, DB_PW, DB_name,
                                  DB_port=DB_port, df_x_y_e=df_x_y_e, ninety_five_percent_error=ninety_five_percent_error)
    
    response_data['response'] = {
        'map_url': Design_Check_1[0],
        'final': Design_Check_1[1].tolist(),
        'areasInd': Design_Check_1[2].tolist(),
        'clusters_labels': Design_Check_1[3].tolist(),
    }
    
    return response_data

if __name__ == '__main__':
    app.run()
