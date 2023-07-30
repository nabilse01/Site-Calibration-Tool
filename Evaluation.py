import psycopg2                               # Importing the psycopg2 library for interacting with PostgreSQL database
import numpy as np                            # Importing the numpy library for array operations
import pandas as pd                           # Importing the pandas library for data manipulation
import math                                   # Importing the math module for mathematical operations
import statistics                             # Importing the statistics module for statistical operations

def perform_density_analysis_fp(venue_id, floor_id, scaleFactor,DB_IP,DB_User,DB_PW,DB_name,DB_port):
    # function to perform density analysis for fingerprint data
    
    wantedData = []                # empty list to store desired data
    probLines = []                 # empty list to store problematic lines
    linesToBeRepeated= []          # empty list to store lines to be repeated
    DB_IP = DB_IP                  # IP address of the database
    DB_User = DB_User              # username to login to the database
    DB_PW = DB_PW                  # password to login to the database
    DB_name = DB_name              # name of the database
    DB_port=DB_port                # port number of the database

    global conn                    # declaring the connection variable as global
    conn = psycopg2.connect(       
        user=DB_User,              # Username for postgresql
        password=DB_PW,            # Password for postgresql
        host=DB_IP,                # Host IP address of postgresql server
        port=DB_port,              # Port number of postgresql server
        database=DB_name           # Name of the database to connect to
    )
    
    global z                       # declaring the z variable as global
    z = 0                          
    
    cur = conn.cursor()             # creating a cursor object for performing database operations

    # Query to fetch fingerprint data from the database
    query = f"SELECT line_order,x,y,time_stamp,cast(major_minor as float) as major_minor,rssi,line_id FROM penguin.tblfp_data WHERE venue_id = {venue_id} AND floor_id = {floor_id};"
    cur.execute(query)              # executing the query
    fp = cur.fetchall()             # fetching all the results of the query
    fp = pd.DataFrame(fp, columns=['line_order', 'x', 'y', 'time_stamp', 'major_minor', 'rssi', 'line_id'])    # creating a dataframe from the fetched results

    major_minor = fp['major_minor']                  # storing the major_minor column in a variable
    macs = np.unique(major_minor)                     # getting unique values of major_minor column
    timestamp = np.unique(fp['time_stamp'])           # getting unique values of time_stamp column
    inx = np.equal.outer(list(fp['time_stamp']), timestamp)   # checking if a value in time_stamp matches each value in list 

    fp_rssi_data = np.zeros((len(timestamp), len(macs)))      # creating an empty array of zeros with shape (len(timestamp), len(macs))
    ordered_fp = np.zeros((len(timestamp), 4))                # creating an empty array of zeros with shape (len(timestamp), 4)
    lineorder = np.zeros((len(timestamp), 1))                 # creating an empty array of zeros with shape (len(timestamp), 1)
    
    for ii in range(inx.shape[1]):
        selected_fp = fp[inx[:, ii]]                        # selecting rows based on index conditions
        selected_fp = selected_fp.reset_index(drop=True)    # reseting the index of the row
        
        # storing unique values of specified columns in a variable
        ordered_fp[ii, :] = np.unique(selected_fp[['line_id', 'x', 'y', 'time_stamp']], axis=0)   
        
        lineorder[ii] = np.unique(fp['line_order'][inx[:, ii]])  # storing unique values of line_order column
        
        rssi = selected_fp['rssi']      # storing the rssi column in a variable
        beacons, index = np.unique(selected_fp['major_minor'], return_index=True)   # getting unique values of major_minor column

        x = np.where(np.isin(macs, beacons))           # getting indices where macs is present in beacons
        fp_rssi_data[ii, x] = rssi[index]

    fp = np.concatenate((ordered_fp, fp_rssi_data, lineorder), axis=1)         # concatenating arrays along a specified axis
    LineIDs = fp[:, 0]                  # storing the first column of the array in a variable
    lineOrder = fp[:, -1]               # storing the last column of the array in a variable
    
    lines = np.unique(lineOrder)          # getting unique values of lineOrder
    
    # Query to fetch sensor data from the database
    
    cur.execute(
        f"SELECT line_order, x, y, orientation_vector_z, line_id, line_timestamp FROM penguin.tblfp_sensors_data WHERE venue_id = {venue_id} AND floor_id = {floor_id} ORDER BY line_timestamp;"
    )
    # Fetch the data from the database and convert it to a numpy array
    data_sensors = cur.fetchall()
    data_sensors = np.array(data_sensors)
    
    # Extract values from specific columns and store them in separate variables
    FP_sensors_line_id = [row[4] for row in data_sensors]
    FP_sensors_line_order = [row[0] for row in data_sensors]
    
    # Extract specific columns from the dataset
    SensorsPoints = data_sensors[:, 1:3]
    
    # Execute a query to fetch floor information
    cur.execute(
        f"SELECT floor_name,map_url FROM penguin.tblfloors WHERE venue_id = {venue_id} AND id = {floor_id} and update_status!=2 ;"
    )
    data_floors = cur.fetchall()
    
    # Extract floor name and map URL from the fetched data
    floorName = [row[0] for row in data_floors][0]
    global map_url
    map_url = [row[1] for row in data_floors][0]
    
    # Check if the number of unique LineIDs is less than the number of unique FP_sensors_line_id
    if len(np.unique(LineIDs)) < len(np.unique(FP_sensors_line_id)):
        ind = np.isin(np.unique(FP_sensors_line_id), np.unique(LineIDs))
        ids = np.unique(FP_sensors_line_id)
        probLines = ids[~ind]
    
    # Extract specific columns from an array
    BLEpoints = fp[:, 1:3]
    
    # Initialize an empty list for wantedData
    wantedData = []
    
    # Iterate over the lines
    for i in lines:
        # Filter the BLEpoints based on the line id
        BLELinePoints = BLEpoints[fp[:, -1] == i, :]
    
        # Filter the SensorsPoints based on the line order
        sensorsLinePoints = SensorsPoints[FP_sensors_line_order == i, :]
    
        # Compute line start and end points
        lineStart = [sensorsLinePoints[0][0], sensorsLinePoints[0][1]]
        LineEnd = [sensorsLinePoints[-1][0], sensorsLinePoints[-1][1]]
    
        # Calculate the number of FPlinePointsCount
        FPlinePointsCount = len(BLELinePoints[:, 0])
    
         # Calculate LineLength
        LineLength = np.linalg.norm(np.array(lineStart) - np.array(LineEnd)) * scaleFactor
    
        # Calculate minNpoints as a percentage of LineLength
        minNpoints = int(np.floor(LineLength - LineLength * 0.1))
    
        # Append the wantedData for this line to the list
        wantedData.append([i, FPlinePointsCount, minNpoints])
    
        # Check if minNpoints is greater than FPlinePointsCount
        if minNpoints > FPlinePointsCount:
            probLines = np.concatenate((probLines, np.unique(LineIDs[lineOrder == i])))
    
    # Iterate over the probLines and add them to linesToBeRepeated list
    for i in probLines:
        linesToBeRepeated.append(i)
    
    # Sort and remove duplicates from linesToBeRepeated
    linesToBeRepeated = sorted(set(linesToBeRepeated))
    
    # Check if probLines is empty
    if len(probLines) == 0:
        pass
        # print(f"The 'FP' for {floorName} passed density analysis")
    else:
        z += 1
        # Sum the occurrences of probLines in data_sensors
        probPoints = np.sum(np.equal.outer(data_sensors[:, 4], linesToBeRepeated), axis=1)
        # print(f"The 'FP' for {floorName} didn't pass density analysis")
    
        # Create a formatted string to display the problematic Line IDs
        formatSpec = "the following Line ID of the FP of {} didn't pass density analysis: \n{}\n".format(
            floorName, ', '.join(map(str, linesToBeRepeated)))
        # print(formatSpec)
    
    # Extract specific columns from data_sensors array
    x_y = data_sensors[:, 1:3]
    
    # Get unique line IDs from data_sensors
    lineIds = np.unique(data_sensors[:, 0])
    
    # Create empty lists for storing line orientations
    lineOrient = []
    orient = []
    
    # Iterate over lineIds and compute line orientations
    for i, lineId in enumerate(lineIds):
        # Filter x_y based on lineId
        indc = data_sensors[:, 0] == lineId
        xys = x_y[indc,:]
    
        # Calculate the vector representing the line
        a = [0, 0]
        a[0] = xys[-1, 0] - xys[0, 0]
        a[1] = xys[-1, 1] - xys[0, 1]
    
        # Calculate the orientation of the line
    
        # Calculate the orientation of a given vector and append it to the lineOrient list
        lineOrient.append(math.atan2(a[1], a[0]))
        
        # Convert the orien list to a numpy array
        orien = np.array(data_sensors[indc, 3])
        
        # Check if values in orien are less than or equal to -180 and update them accordingly
        orienLessThan180 = (orien <= -180)
        orien[orienLessThan180] += 360
        
        # Check if values in orien are greater than 180 and update them accordingly
        orienMoreThan180 = (orien > 180)
        orien[orienMoreThan180] -= 360
        
        # Find indices where values in orien are between 90 and 180
        ind = np.where((orien > 90) & (orien < 180))[0]
        
        # If any such indices are found
        if len(ind) > 0:
            # Find indices where values in orien are between -90 and -180
            ind = np.where((orien < -90) & (orien > -180))[0]
            # Add 360 to the values at those indices
            orien[ind] += 360
        
        # Append the mean value of orien to the orient list
        orient.append(statistics.mean(orien))
        
        # Convert the values in lineOrient from radians to degrees
        lineOrient = np.rad2deg(lineOrient)
        
        # Convert lineOrient to a numpy array
        lineOrient = np.array(lineOrient)
        
        # Add 360 to the values in lineOrient that are less than 0
        lineOrient[lineOrient < 0] += 360
        
        # Convert the values in orient to a numpy array
        orient = np.array(orient)
        
        # Convert the values in lineOrient to a numpy array
        lineOrient = np.array(lineOrient)
        
        # Add 360 to the values in orient that are less than 0
        orient[orient < 0] += 360
        
        # Calculate the difference between orient and lineOrient and assign it to mapnorth_vector
        mapnorth_vector = orient - lineOrient
        
        # Add 360 to the values in mapnorth_vector that are less than 0
        mapnorth_vector[mapnorth_vector < 0] += 360
        
        # Calculate the median of mapnorth_vector and assign it to mapnorth
        mapnorth = np.median(mapnorth_vector)
        
        # Subtract mapnorth from orient and assign it to adjOrien1 
        adjOrien1 = orient - mapnorth
        
        # Add 360 to the values in adjOrien1 that are less than 0
        adjOrien1[adjOrien1 < 0] += 360
        
        # Calculate the absolute difference between adjOrien1 and lineOrient and assign it to diff
        diff = abs((adjOrien1) - lineOrient)
        
        # Find indices where diff is greater than 150 and less than 300 and add 1 to them
        errors = np.where((diff > 150) & (diff < 300))[0] + 1
        
        # If there are any errors found
        if len(errors) != 0:
            # Increment the value of z by 1
            z += 1
            # Find the indices where data_sensors[:, 0] is equal to errors
            x = np.sum(np.equal.outer(data_sensors[:, 0], errors), axis=1)
            # Extend linesToBeRepeated with unique values from data_sensors[x.astype(bool), 4]
            linesToBeRepeated.extend(np.unique(data_sensors[x.astype(bool), 4]))
        
        # If linesToBeRepeated has any elements
        if len(linesToBeRepeated) > 0:
            # Deduplicate the values in linesToBeRepeated and assign it back to linesToBeRepeated as a list
            linesToBeRepeated = list(set(linesToBeRepeated))
            # Print the message with flattened_values containing line IDs to be repeated
            # print(f"Repeat the following Line IDs in {floorName}:")
            flattened_values = ", ".join(map(str, linesToBeRepeated))
            # print(flattened_values)
            # Convert linesToBeRepeated to a numpy array
            linesToBeRepeated = np.array(linesToBeRepeated)
            # Calculate the sum of values where data_sensors[:, 4] is equal to linesToBeRepeated and assign it to probPoints
            probPoints = np.sum(np.equal.outer(data_sensors[:, 4], linesToBeRepeated), axis=1)
            # Return map_url, data_sensors, probPoints, linesToBeRepeated, and z
            return map_url, data_sensors, probPoints, linesToBeRepeated, z
        
        # If linesToBeRepeated is empty
        else:
            # Return None
            return None 
        

def perform_density_analysis_sig(venue_id, floor_id, scaleFactor, DB_IP, DB_User, DB_PW, DB_name,DB_port):
    """
    Perform density analysis on signature data for a specific venue and floor.

    Args:
        venue_id (int): ID of the venue.
        floor_id (int): ID of the floor.
        scaleFactor (float): Scale factor for LineLength.
        DB_IP (str): IP address of the database.
        DB_User (str): Username to login to the database.
        DB_PW (str): Password to login to the database.
        DB_name (str): Name of the database to connect to.
        DB_port (int): Port number of the postgresql server.

    Returns:
        tuple: A tuple containing map_url, data_sensors, probPoints, sig_names, stop.

    """

    wantedData = []
    probLines = []
    DB_IP = DB_IP  # IP address of the database
    DB_User = DB_User  # username to login to the database
    DB_PW = DB_PW  # password to login to the database
    DB_name = DB_name
    DB_port=DB_port

    # Establish database connection
    global conn
    conn = psycopg2.connect(
        user=DB_User,           # Username for postgresql
        password=DB_PW,         # Password for postgresql
        host=DB_IP,             # Host IP address of postgresql server
        port=DB_port,            # Port number of postgresql server
        database=DB_name        # Name of the database to connect to
    )

    linesToBeRepeated = []
    line_id_to_sig_names = {}
    stop = 'False'

    cur2 = conn.cursor()

    # Fetching distinct sig_ids based on venue_id and floor_id
    cur2.execute(
        f"SELECT DISTINCT sig_id FROM penguin.tblsignature_data WHERE venue_id = {venue_id} AND floor_id = {floor_id}"
    )
    global sig_ids
    sig_ids = [row[0] for row in cur2.fetchall()]

    # Iterate over each sig_id
    for sig_id in sig_ids:
        query = f"SELECT line_order,x,y,time_stamp,cast(major_minor as float) as major_minor,rssi,line_id,sig_name FROM penguin.tblsignature_data WHERE venue_id = {venue_id} AND floor_id = {floor_id} and sig_id = {sig_id} ;"

        # Execute the query to fetch signature data
        cur2.execute(query)
        sig = cur2.fetchall()
        sig_origin = pd.DataFrame(sig, columns=[
            'line_order', 'x', 'y', 'time_stamp', 'major_minor', 'rssi', 'line_id','sig_names'])

        # Perform calculations on the fetched signature data
        major_minor = sig_origin['major_minor']
        macs = np.unique(major_minor)
        timestamp = np.unique(sig_origin['time_stamp'])
        inx = np.equal.outer(list(sig_origin['time_stamp']), timestamp)
        sig_rssi_data = np.zeros((len(timestamp), len(macs)))
        ordered_sig = np.zeros((len(timestamp), 4))
        lineorder = np.zeros((len(timestamp), 1))

        for ii in range(inx.shape[1]):
            selected_sig = sig_origin[inx[:, ii]]
            selected_sig = selected_sig.reset_index(drop=True)
            ordered_sig[ii, :] = np.unique(
                selected_sig[['line_id', 'x', 'y', 'time_stamp']], axis=0)
            lineorder[ii] = np.unique(sig_origin['line_order'][inx[:, ii]])
            rssi = selected_sig['rssi']
            beacons, index = np.unique(
                selected_sig['major_minor'], return_index=True)

            x = np.where(np.isin(macs, beacons))
            sig_rssi_data[ii, x] = rssi[index]

        # Concatenate the calculated data to get final signature information
        sig = np.concatenate((ordered_sig, sig_rssi_data, lineorder), axis=1)
        LineIDs = sig[:, 0]
        lineOrder = sig[:, -1]
        lines = np.unique(lineOrder)

        # Fetch additional sensor data for the specified venue and floor
        cur2.execute(
            f"SELECT line_order, x, y, orientation_vector_z, line_id, line_timestamp FROM penguin.tblsignature_sensors_data WHERE venue_id = {venue_id} AND floor_id = {floor_id} and sig_id = {sig_id} ORDER BY line_timestamp;"
        )
        data_sensors = cur2.fetchall()
        data_sensors = np.array(data_sensors)
        sig_sensors_line_id = [row[4] for row in data_sensors]
        sig_sensors_line_order = [row[0] for row in data_sensors]
        SensorsPoints = data_sensors[:, 1:3]

        cur2.execute(
            f"SELECT floor_name,map_url FROM penguin.tblfloors WHERE venue_id = {venue_id} AND id = {floor_id} and update_status!=2;"
        )

        # Execute SQL query to fetch floor name and map URL based on venue ID and floor ID
        cur2.execute(
            f"SELECT floor_name,map_url FROM penguin.tblfloors WHERE venue_id = {venue_id} AND id = {floor_id} and update_status!=2;"
        )
        
        # Fetch the data from the executed query
        data_floors = cur2.fetchall()
        
        # Extract the floor name and map URL from the fetched data
        floorName = [row[0] for row in data_floors][0]
        map_url = [row[1] for row in data_floors][0]
        
        # Check if the number of unique LineIDs is less than the number of unique sig_sensors_line_id
        if len(np.unique(LineIDs)) < len(np.unique(sig_sensors_line_id)):
            ind = np.isin(np.unique(sig_sensors_line_id), np.unique(LineIDs))
            ids = np.unique(sig_sensors_line_id)
            probLines = ids[~ind]
        
        # Extract BLE points (columns 1 and 2) from sig array
        BLEpoints = sig[:, 1:3]
        wantedData = []
        
        # Iterate over lines
        for i in lines:
            # Select BLE points based on current line
            BLELinePoints = BLEpoints[sig[:, -1] == i, :]
            sensorsLinePoints = SensorsPoints[sig_sensors_line_order == i, :]
            lineStart = [sensorsLinePoints[0][0], sensorsLinePoints[0][1]]
            LineEnd = [sensorsLinePoints[-1][0], sensorsLinePoints[-1][1]]
            
            # Count the number of points in the BLE line
            siglinePointsCount = len(BLELinePoints[:, 0])
        
            LineLength = np.linalg.norm(np.array(lineStart) - np.array(LineEnd)) * scaleFactor
            minNpoints = int(np.floor(LineLength - LineLength * 0.1))
        
            wantedData.append([i, siglinePointsCount, minNpoints])
            
            # Check if the minimum number of points required is greater than the actual number of points
            if minNpoints > siglinePointsCount:
                probLines = np.concatenate((probLines, np.unique(LineIDs[lineOrder == i])))
        
        # Add lines to linesToBeRepeated list
        for i in probLines:
            linesToBeRepeated.append(i)
            
        # Sort and remove duplicates from linesToBeRepeated list
        linesToBeRepeated = sorted(set(linesToBeRepeated))
        
        # If no lines need to be repeated, do nothing
        if len(linesToBeRepeated) == 0:
            pass
            # print(f"The 'Sig' for {floorName} passed density analysis")
        else:
            stop = 'True'
            
            # Calculate the number of problematic points for each line
            probPoints = np.sum(np.equal.outer(data_sensors[:, 4], linesToBeRepeated), axis=1)
            
            # Print the lines that didn't pass density analysis
            formatSpec = "the following Line ID of the Sig of {} didn't pass density analysis: \n{}\n".format(floorName, ', '.join(map(str, linesToBeRepeated)))
            # print(formatSpec)
        
        # Extract x and y coordinates from data_sensors
        x_y = data_sensors[:, 1:3]
        lineIds = np.unique(data_sensors[:, 0])
        b = np.array([1, 0])
        a = np.zeros(2)
        lineOrient = []
        orient = []
        
        # Iterate over line IDs
        for i in lineIds:
            indc = data_sensors[:, 0] == i
            xys = x_y[indc, :]
        
            a = [xys[-1, 0] - xys[0, 0], xys[-1, 1] - xys[0, 1]]
            lineOrient.append(np.arctan2(a[1], a[0]))
            
            orien = np.array(data_sensors[indc, 3])
            orienLessThan180 = (orien <= -180)
            orienMoreThan180 = (orien > 180)
        
            orien[orienLessThan180] += 360
            orien[orienMoreThan180] -= 360
            
            # Adjust orientation values outside the -90 to 90 range
            ind = np.where(np.logical_and(orien > 90, orien < 180))[0]
            if ind.size != 0:
                ind2 = np.where(np.logical_and(orien < -90, orien > -180))[0]
                orien[ind2] += 360
        
            orient.append(statistics.mean(orien))
        
            # Convert the values in lineOrient from radians to degrees
            lineOrient = np.rad2deg(lineOrient)
            
            # Convert lineOrient to a numpy array
            lineOrient = np.array(lineOrient)
            
            # Add 360 to the values in lineOrient that are less than 0
            lineOrient[lineOrient < 0] += 360
            
            # Convert the values in orient to a numpy array
            orient = np.array(orient)
            
            # Convert the values in lineOrient to a numpy array
            lineOrient = np.array(lineOrient)
            
            # Add 360 to the values in orient that are less than 0
            orient[orient < 0] += 360
            
            # Calculate the difference between orient and lineOrient and assign it to mapnorth_vector
            mapnorth_vector = orient - lineOrient
            
            # Add 360 to the values in mapnorth_vector that are less than 0
            mapnorth_vector[mapnorth_vector < 0] += 360
            
            # Calculate the median of mapnorth_vector and assign it to mapnorth
            mapnorth = np.median(mapnorth_vector)
            
            # Subtract mapnorth from orient and assign it to adjOrien1 
            adjOrien1 = orient - mapnorth
            
            # Add 360 to the values in adjOrien1 that are less than 0
            adjOrien1[adjOrien1 < 0] += 360
            
            # Calculate the absolute difference between adjOrien1 and lineOrient and assign it to diff
            diff = abs((adjOrien1) - lineOrient)
            
            # Find indices where diff is greater than 150 and less than 300 and add 1 to them
            errors = np.where((diff > 150) & (diff < 300))[0] + 1 
            if len(errors) > 0:  # If there are indices found
                stop = 'True'  # Set stop variable to 'True'
                x = np.sum(np.equal.outer(sig_sensors_line_order, errors), axis=1)  # Compare sig_sensors_line_order with errors array and sum the results
                linesToBeRepeated.extend(np.unique(data_sensors[x.astype(bool), 4]))  # Add unique values from data_sensors to linesToBeRepeated based on x
            
            if len(linesToBeRepeated) > 0:  # If there are items in linesToBeRepeated
                linesToBeRepeated = list(set(linesToBeRepeated))  # Remove duplicate values from linesToBeRepeated
            
                flattened_values = ", ".join(map(str, linesToBeRepeated))  # Convert linesToBeRepeated to a comma-separated string
                linesToBeRepeated = list(set(linesToBeRepeated))  # Remove duplicate values from linesToBeRepeated again
            
                linesToBeRepeated = np.array(linesToBeRepeated)  # Convert linesToBeRepeated to a numpy array
                probPoints = np.sum(np.equal.outer(data_sensors[:, 4], linesToBeRepeated), axis=1)  # Compare data_sensors with linesToBeRepeated and sum the results
                for index, row in sig_origin.iterrows():  # Iterate over rows in sig_origin dataframe
                    line_id = row['line_id']  # Get the value of 'line_id' column
                    sig_names = row['sig_names']  # Get the value of 'sig_names' column
                    line_id_to_sig_names[line_id] = sig_names  # Assign sig_names to line_id in line_id_to_sig_names dictionary
            
            sig_names = set([line_id_to_sig_names[line_id] for line_id in LineIDs])  # Get the unique sig_names for each line_id in LineIDs
            sig_names = np.array(list(sig_names))  # Convert the set of sig_names to a numpy array
            
            return map_url, data_sensors, probPoints, sig_names, stop  # Return the values map_url, data_sensors, probPoints, sig_names, and stop
            
    else :
        return None


