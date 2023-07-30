# import required libraries and modules
import Payload     
import json
import requests
import math
import numpy as np
import matplotlib.pyplot as plt
import ujson as json   
import psycopg2          
import datetime
import time




# This code creates an HTTPAdapter instance with a maximum number of retries of 50, which will be used by the requests.Session object for both http and https requests.
adapter = requests.adapters.HTTPAdapter(max_retries=1000)

# A session is created which we'll use to manage and persist parameters across multiple requests.
session = requests.Session()

# The HTTP adapter is mounted to the "https://" and "http://" protocols in order to provide the retry behavior.
session.mount("https://", adapter)
session.mount("http://", adapter)

# An empty list called diff_F is initialized
diff_F = []

# RawConfigParser() instance is created and loads database details from config.properties file.


# The PE url is retrieved from the config file using 'get' method.

# Request headers indicating the content-type of the data sent to the server are defined.
headers = {'Content-Type': 'application/json'}
k=0
# DB_IP, DB_User, DB_PW and DB_name variables are stored with corresponding values read from the configuration file.

# This function gets signature ids based on the supplied venue id and floor id

def get_data(venue_id, floor_id, sig_id):
    """
    This function gets data from the penguin.tblsignature_data table.

    Args:
      venue_id: The ID of the venue.
      floor_id: The ID of the floor.
      sig_id: The ID of the signature.

    Returns:
      A list of tuples containing the timestamp, major_minor, rssi, x, and y values.
    """

    try:
        # Open a cursor to the database.
        cursor = conn.cursor()

        # Execute the SQL query.
        cursor.execute(
            f"SELECT time_stamp, major_minor, rssi, x, y FROM penguin.tblsignature_data WHERE venue_id = {venue_id} AND floor_id = {floor_id} AND sig_id = {sig_id} ORDER BY time_stamp ASC  ")

        # Fetch the results.
        results = cursor.fetchall()

        # Close the cursor.
        cursor.close()

        # Return the results.
        return results

    except (Exception, psycopg2.Error) as error:
        # Print the error message.
        print(error)

def get_list(venue_id,floor_id,sig_id):
    readings_for_all_sigs = {}

    # Get the data from the database
    data = get_data(venue_id, floor_id, sig_id)

    # Iterate over each row and process the data
    for row in data:
        time_stamp, major_minor, rssi, x, y = row
        if time_stamp not in readings_for_all_sigs:
            readings_for_all_sigs[time_stamp] = []
        readings_for_all_sigs[time_stamp].append((major_minor, rssi, x, y))
    # Convert the dictionary to a list of lists
    readings_for_all_sigs = list(readings_for_all_sigs.values())

    return readings_for_all_sigs

def get_readings_for_all_sigs(venue_id, floor_id):
    all_sig_readings = {}
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT sig_id FROM penguin.tblsignature_data WHERE venue_id = {venue_id} AND floor_id = {floor_id}")
    global sig_ids
        # Get the sig_ids from the fetched rows returned by the query execution
    sig_ids = [row[0] for row in cursor.fetchall()]
    # Get the list of sig_ids for the given venue_id and floor_id

    # Iterate over each sig_id and collect the readings
    for sig_id in sig_ids:
        sig_readings = get_list(venue_id, floor_id, sig_id)
        all_sig_readings[sig_id] = sig_readings
    sorted_sig_readings = {k: v for k, v in sorted(all_sig_readings.items(), key=lambda item: len(item[1]), reverse=True)}

    return sorted_sig_readings
 
def send_payload(sig_id,data1,j,scale_factor,floor_id, Param_MaxParticlesM, Param_minParticlesM, Param_distSTDM, Param_bleRSSIcutOffM):

            req = 1 
            global z 
            z= 0
            Data = ''
            sig_id_n = f'{sig_id}_{j}_{Param_MaxParticlesM}_{Param_minParticlesM}_{Param_distSTDM}_{Param_bleRSSIcutOffM}'
            # This is another loop to iterate through all the records present in readings variable.
            diff_list = []
            for record in  data1 : 
                # Joining each 2 elements of record with ',' separator and adding '_2' at the end of each joined element and concatenating them with Data variable.
                Data = ''.join(
                    [f"{elemet[0]},{elemet[1]},2_" for elemet in record])
            # Set the data for the EP object by retrieving all of the Data except for the last character
                EP = Payload.GetEP_Payload
                EP.data = Data[:-1]
                # Set various attributes for the EP object based on given values or converted to string
                EP.session_id = str(sig_id_n)
                EP.user_id = str(sig_id_n)
                EP.fix_floor_id = str(floor_id) 
                EP.orientation = "0"
                EP.barometer_reading = "0"
                EP.req_id = str(req)
                EP.steps_count = "2"
                EP.heading = "0"
                EP.orientation_status = "1"
                EP.accelerometer_status = "1"

                # Set is_wi_fi and reset_particles flags to False
                EP.is_wi_fi = False
                EP.reset_particles = False

                # Set a specific device_id for this EP object, which may be hardcoded
                EP.device_id = "88755444"

                # Set trigger_venue_detection flag to False
                EP.trigger_venue_detection = False

                # Set three values related to particle settings:
                # maxParticlesSettings, minParticlesSettings, and rssiCutOffLimitSettings
                EP.maxParticlesSettings = Param_MaxParticlesM
                EP.minParticlesSettings = Param_minParticlesM
                EP.rssiCutOffLimitSettings = Param_bleRSSIcutOffM
                # Set the standardDeviationSettings to a value based on Param_distSTDM
                EP.standardDeviationSettings = Param_distSTDM
                            # # Converting the object to a JSON string

                payload2 = json.dumps(EP.to_dict(EP))

                # # Making a POST request with URL, Headers and Payload data
                start = datetime.datetime.now()
                response = session.post(url, headers=headers, data=payload2)
                req = req + 1

                mylist = response.text.split(",")
                if  isinstance(mylist[3].encode('utf-8'), int):      
                    pass    
                else : 
                    
                # Getting float value at index 2 from the mylist, converting it to float datatype and storing in 'my_float_val'
                    my_float_val_1 = float(mylist[2].encode('utf-8' ))
                    # Getting float value at index 2 from the mylist, converting it to float datatype and storing in 'my_float_val'
                    my_float_val_2 = float(mylist[3].encode('utf-8'))
                    # Evaluating the conditions for the variable 'my_float_val'
                    if my_float_val_1 == -1 or my_float_val_1 == -2 or  my_float_val_2 == -1 or my_float_val_2 == -2:
                        # If the condition satisfies, then pass it
                        sig_results.append(-1000)
                    else:
                        if response.text.find("-1000") != -1:
                            # If the condition satisfies, then pass it
                            pass
                        else:              
                            # Calculating the difference between two float values using the hypot method of Math class, multiplying with scaling factor and store the resulted differential value.
                            diff = math.hypot(float(list(element[2] for element in record)[0]) - float(mylist[2].encode('utf-8')),
                                                float(list(element[3] for element in record)[0]) - float(mylist[3].encode('utf-8'))) * scale_factor
                            # Checking whether the diff is NOT None, If NOT appending the diff to diff_F list.
                            if diff is not None:
                                sig_results.append(diff)
                                error_values.append(diff)
                                x_values.append(float(list(element[2] for element in record)[0]))
                                y_values.append(float(list(element[3] for element in record)[0]))
            return sig_results
              
def final(venue_id, floor_id, montecarloIter, scale_factor, MaxParticlesM, minParticlesM, distSTDM, bleRSSIcutOffM,DB_IP,DB_User,DB_PW,DB_name,PE_Url,DB_port):
    DB_IP = DB_IP # IP address of the database
    DB_User = DB_User  # username to login to the database
    DB_PW = DB_PW  # password to login to the database
    DB_name = DB_name
    PE_Url = PE_Url
    DB_port=DB_port
    global url
    url = PE_Url+'PEService.svc/GetEP'
    global conn
    conn = psycopg2.connect(
        user=DB_User,           # Username for postgresql
        password=DB_PW,         # Password for postgresql
        host=DB_IP,             # Host IP address of postgresql server
        port=DB_port,            # Port number of postgresql server
        database=DB_name        # Name of the database to connect to
    )
    readings_for_all_sigs = get_readings_for_all_sigs(venue_id,floor_id)

    DiffAll = [] # creating an empty list named DiffAll that may be appended later on
    # declaring a global variable z outside the function body
    global z
    # assigning infinity to the min_sum variable
    min_sum = float('inf')

    # creating a list comprehension to create a new list of tuples z.
    z = [(a, b, c, d) for a in MaxParticlesM
         for b in minParticlesM
         for c in distSTDM
         for d in bleRSSIcutOffM
         if b < a]
    
    start = datetime.datetime.now()
    # calling start_thread function and passing four parameters venue_id,floor_id,montecarloIter,scale_factor
    result = start_threads(venue_id, floor_id, montecarloIter, scale_factor,z,readings_for_all_sigs)    # start_threads(venue_id, floor_id, montecarloIter, scale_factor)
    end2 = datetime.datetime.now()
    end_2 = end2 - start
    print(end_2)

    # The following code calculates statistics for each list in a nested dictionary, result.
    for combination, lists in result.items():

        # Create two empty dictionaries to hold the statistical information
        result_with_stats = {}
        # Sort the lists in ascending order using NumPy
        sorted_list = np.sort(lists[0])
        # Calculate the maximum, minimum, standard deviation, mean and median values of the sorted list
        max_value = np.max(sorted_list)
        min_value = np.min(sorted_list)
        std_value = np.std(sorted_list)
        mean_value = np.mean(sorted_list)
        median_value = np.median(sorted_list)
        
        # Scale the list to have values between 0 and 1 using linspace function
        yvals = np.arange(len(sorted_list))/float(len(sorted_list)-1)

        # Find the index and value at the 90th percentile of the sorted list
        idx_of_90th_percentile = next(
            i for i, x in enumerate(yvals) if x >= 0.9)
        value_at_90th_percentile = sorted_list[idx_of_90th_percentile]

        # Find the index and value at the 95th percentile of the sorted list
        idx_of_95th_percentile = next(
            i for i, x in enumerate(yvals) if x >= 0.95)
        value_at_95th_percentile = sorted_list[idx_of_95th_percentile]

        # Fill the 'result_with_stats' dictionary with calculated statistical values
        result_with_stats[combination] = {
            'sorted_list': sorted_list,
            'max': max_value,
            'min': min_value,
            'std': std_value,
            'mean': mean_value,
            'median': median_value,
            'yvals': yvals,
            'idx_of_90th_percentile': idx_of_90th_percentile,
            'value_at_90th_percentile': value_at_90th_percentile,
            'idx_of_95th_percentile': idx_of_95th_percentile,
            'value_at_95th_percentile': value_at_95th_percentile,
            'x_values':lists[1],
            'y_values':lists[2]
        }
        # Loop over the key-value pairs in `result_with_stats` dictionary
        for key, value in result_with_stats.items():


            # Calculate the sum of specific values in the nested dictionary `value`
            curr_sum = value['max'] + value['min'] + value['std'] + value['mean'] + \
                value['median'] + value['value_at_90th_percentile'] + \
                value['value_at_95th_percentile']

   
            # Compare the current sum with the minimum sum (`min_sum`) found previously. If the current sum is smaller, then update `min_sum` and `min_sum_key`.
            if curr_sum < min_sum:
                min_sum = curr_sum
                min_sum_key = key

            # Get the sorted list from the nested dictionary `value`
            DiffAll = value['sorted_list']
            x_values = value['x_values']
            y_values = value['y_values']

            # Create an array representing the fraction of data points below the corresponding value in the sorted list.
            yvals_F = np.arange(len(DiffAll))/float(len(DiffAll)-1)

            # Find the maximum value in the sorted list
            max_error_D = max(DiffAll)
            


        # Return DiffAll (the sorted list), max_error_D (the maximum value in the sorted list), value (the last value iteration of the original loop through the dictionary), and min_sum_key (the key associated with the minimum sum computed during the loop).

    return DiffAll, max_error_D, value, min_sum_key,x_values,y_values



# define a function that simulates sending a request

import concurrent.futures
def start_threads(venue_id, floor_id, montecarloIter, scale_factor, z,readings_for_all_sigs):
    # declare global variables to use inside the function
    global add
    global lists
    global result
    
    result = {}
    # set initial value for add variable to 1
    add = 1
    # initialize lists as an empty list
    lists = []
    
    # get signal IDs based on venue ID and floor ID provided
    # create a dictionary to hold results for each signal ID
    

    
    # create a list to hold threads
    result_dict = {}
    
   # loop through the number of Monte Carlo simulations to be performed
    global combination
    req=1
    
    for combination in z:
        
        threads=[]
        global sig_results_list
        global results
        results = []
        # Get integers from the nested list 'combination' and store them in separate variables
        Param_MaxParticlesM = int(combination[0])
        Param_minParticlesM = int(combination[1])
        Param_distSTDM = int(combination[2])
        Param_bleRSSIcutOffM = int(combination[3])
        # Pass the obtained parameters to the start_threads() function 
        global x_values
        global y_values
        global error_values
        global sig_results
        sig_results=[]
        x_values = []
        y_values = []
        error_values = []
        
        sig_results_list = []
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=10000)

        futures = [
            executor.submit(
                lambda: (
                    send_payload(sig_id, data1, repeat, scale_factor, floor_id, Param_MaxParticlesM, Param_minParticlesM,
                                Param_distSTDM, Param_bleRSSIcutOffM),
                    time.sleep(0.01)  # Introduce 0.01 seconds delay after each submit
                )
            )
            for sig_id, data1 in readings_for_all_sigs.items()
            for repeat in range(montecarloIter)
        ]

        concurrent.futures.wait(futures)

        def split_list_into_chunks(list_to_split, num_of_chunks):
            """Splits a list into a number of lists with equal values on each other.

            Args:
                list_to_split: The list to split.
                num_of_chunks: The number of lists to split the original list into.

            Returns:
                A list of lists, where each sublist contains equal values.
            """

            sublists = []
            chunk_size = len(list_to_split) // num_of_chunks
            for i in range(num_of_chunks):
                start_index = i * chunk_size
                end_index = (i + 1) * chunk_size
                sublists.append(list_to_split[start_index:end_index])
            return sublists

        def get_max_columns(lists):
            max_values = []
            for column in zip(*lists):
                max_val = max(column)
                max_values.append(max_val)

            return max_values
       
        sublists = split_list_into_chunks(sig_results, montecarloIter)

        max_columns = get_max_columns(sublists)
        max_columns = [value for value in max_columns if value >= 0]

        # result[combination] = max_columns
        data = {"x": x_values, "y": y_values, "error_values": error_values}
        result_x_y_e = [d for d in data["error_values"] if d in max_columns]
        x_result = [data["x"][i] for i in range(len(data["error_values"])) if data["error_values"][i] in result_x_y_e]
        y_result = [data["y"][i] for i in range(len(data["error_values"])) if data["error_values"][i] in result_x_y_e]
        lists = [max_columns, x_result, y_result]
        result[combination] = [max_columns, x_result, y_result]

    return result
    