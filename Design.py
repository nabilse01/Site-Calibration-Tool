# Import the necessary modules to connect to a database, read configuration files, and work with data
import psycopg2  # module to connect to PostgreSQL databases
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def Design_Check(venue_id, floor_id, scale_factor, DB_IP, DB_User, DB_PW, DB_name, DB_port, df_x_y_e, ninety_five_percent_error):
    # Filter the data based on error values greater than the given threshold
    filtered_data = df_x_y_e[df_x_y_e['error_values']
                             > ninety_five_percent_error]
    filtered_x_y = filtered_data[['x_values', 'y_values']]

    clusterThreshold = 3  # meters
    minNumberOfPoints = 4

    DB_IP = DB_IP  # IP address of the database
    DB_User = DB_User  # username to login to the database
    DB_PW = DB_PW  # password to login to the database
    DB_name = DB_name
    DB_port = DB_port

    # Try to establish a connection with the PostgreSQL database using the parameters extracted above
    global conn
    conn = psycopg2.connect(
        user=DB_User,           # Username for PostgreSQL
        password=DB_PW,         # Password for PostgreSQL
        host=DB_IP,             # Host IP address of PostgreSQL server
        port=DB_port,            # Port number of PostgreSQL server
        database=DB_name        # Name of the database to connect to
    )

    cur2 = conn.cursor()
    # Fetch the floor_name and map_url from the penguin.tblfloors table for the given venue_id and floor_id
    cur2.execute(
        f"SELECT floor_name,map_url FROM penguin.tblfloors WHERE venue_id = {venue_id} AND id = {floor_id} and update_status!=2;"
    )
    data_floors = cur2.fetchall()
    map_url = [row[1] for row in data_floors][0]

    global z
    z = 0

    # Create a Cursor object to execute SQL commands on this connection
    cur = conn.cursor()

    query = f"SELECT line_order,x,y,time_stamp,cast(major_minor as float) as major_minor,rssi,line_id FROM penguin.tblfp_data WHERE venue_id = {venue_id} AND floor_id = {floor_id};"

    # Execute the SQL query and fetch all the data from the penguin.tblfp_data table
    cur.execute(query)
    fp = cur.fetchall()
    fp = pd.DataFrame(fp, columns=[
                      'line_order', 'x', 'y', 'time_stamp', 'major_minor', 'rssi', 'line_id'])

    major_minor = fp['major_minor']
    macs = np.unique(major_minor)
    timestamp = np.unique(fp['time_stamp'])
    inx = np.equal.outer(list(fp['time_stamp']), timestamp)
    fp_rssi_data = np.zeros((len(timestamp), len(macs)))
    ordered_fp = np.zeros((len(timestamp), 4))
    lineorder = np.zeros((len(timestamp), 1))

    # Process the fetched data to get required format for analysis
# Iterate over the columns of the "inx" array
    for ii in range(inx.shape[1]):
        # Select the rows from "fp" based on the boolean values in the ii-th column of "inx"
        selected_fp = fp[inx[:, ii]]
        
        # Reset the index of the selected rows and assign the result to "selected_fp"
        selected_fp = selected_fp.reset_index(drop=True)
        
        # Get unique rows of "selected_fp" based on columns 'line_id', 'x', 'y', 'time_stamp' 
        # and assign the result to row ii of the "ordered_fp" array
        ordered_fp[ii, :] = np.unique(selected_fp[['line_id', 'x', 'y', 'time_stamp']], axis=0)
        
        # Get unique values of 'line_order' column in "fp" for the selected rows
        # based on the boolean values in the ii-th column of "inx" and assign the result 
        # to element ii of the "lineorder" array
        lineorder[ii] = np.unique(fp['line_order'][inx[:, ii]])
        
        # Retrieve the 'rssi' values from the selected rows and assign them to the "rssi" variable
        rssi = selected_fp['rssi']
        
        # Get unique values of 'major_minor' column in "selected_fp" and return their indices
        # into the "beacons" and "index" arrays respectively
        beacons, index = np.unique(selected_fp['major_minor'], return_index=True)
        
        # Find the indices of elements in "macs" array that match the elements in "beacons" array
        # and assign the result to the "x" variable
        x = np.where(np.isin(macs, beacons))
        
        # Assign the "rssi" values at the "index" positions in the "fp_rssi_data" array
        # for the current ii-th column to the "x" indices in the same column
        fp_rssi_data[ii, x] = rssi[index]

    # Concatenate "ordered_fp", "fp_rssi_data", and "lineorder" along the second axis into "fp"
    fp = np.concatenate((ordered_fp, fp_rssi_data, lineorder), axis=1)

    # Slice "fp" array from column index 4 up to, but excluding, the last column, 
    # assign it to "fp_temp" variable
    fp_temp = fp[:, 4:-1]

    # Replace all occurrences of 0 with -200 in "fp_temp" array
    fp_temp[fp_temp == 0] = -200

    # Find the maximum value along each row of "fp_temp" and assign the result to "max_reading" array
    max_reading = np.max(fp_temp, axis=1)

    # Find the indices of the maximum values in each row of "fp_temp" and assign the result to "index" array
    index = np.argmax(fp_temp, axis=1)

    # Initialize a boolean array "RuleCheck" with shape (len(fp_temp), 3) filled with False values
    RuleCheck = np.zeros((len(fp_temp), 3), dtype=bool)

    # Set the first column of "RuleCheck" to True where the corresponding value in "max_reading" is greater than or equal to -79
    RuleCheck[:, 0] = max_reading >= -79

    # Convert "fp_temp.shape" to a NumPy array and assign it to "sz" variable
    sz = np.asarray(fp_temp.shape)

    # Create an array "x" containing multi-dimensional indices 
    # corresponding to the elements in "sz[0]" range and "index" array
    x = np.ravel_multi_index((np.arange(sz[0]), index), dims=sz)

    # Set the elements in "fp_temp" array at the locations specified by "x" to -200
    fp_temp.flat[x] = -200

    # Find the maximum value along each row of the updated "fp_temp" and assign the result to "max_reading" array
    max_reading = np.max(fp_temp, axis=1)

    # Find the indices of the maximum values in each row of the updated "fp_temp" and assign the result to "index" array
    index = np.argmax(fp_temp, axis=1)

    # Set the second column of "RuleCheck" to True where the corresponding value in "max_reading" is greater than or equal to -84
    RuleCheck[:, 1] = max_reading >= -84

    # Convert "fp_temp.shape" to a NumPy array again and assign it to "sz" variable
    sz = np.asarray(fp_temp.shape)

    # Create an array "x" containing multi-dimensional indices 
    # corresponding to the elements in "sz[0]" range and "index" array
    x = np.ravel_multi_index((np.arange(sz[0]), index), dims=sz)

    # Set the elements in " 

    fp_temp.flat[x] = -200

    RuleCheck[:, 2] = max_reading >= -84

    sz = np.asarray(fp_temp.shape)  # Convert the shape of the array variable fp_temp to a NumPy array and assign it to sz
    
    x = np.ravel_multi_index((np.arange(sz[0]), index), dims=sz)  # Compute the linear index equivalent to the given tuple (np.arange(sz[0]), index) using the shape of sz and assign it to x
    
    fp_temp.flat[x] = -200  # Set the value at index x in the flattened version of fp_temp to -200
    
    RuleOfThumpCheck = np.sum(RuleCheck, axis=1) >= 3  # Check if the sum of each row in RuleCheck is greater than or equal to 3 and assign the resulting boolean array to RuleOfThumpCheck
    
    points = fp[np.logical_not(RuleOfThumpCheck), 1:3]  # Create a new array 'points' by selecting rows from fp where the corresponding element in RuleOfThumpCheck is False, and columns 1 and 2
    
    final = np.concatenate((filtered_x_y, points))  # Concatenate arrays filtered_x_y and points along the first dimension and assign the result to final
    
    if len(final) == 0:  # Check if the length of final is 0
        return None  # Return None if final is an empty array
    else:
        clusters = DBSCAN(eps=clusterThreshold/scale_factor, min_samples=minNumberOfPoints).fit(final)  # Apply DBSCAN clustering algorithm to the dataset 'final' with given epsilon and minimum number of points, and assign the resulting clusters object to clusters
    
        areasInd = np.where(clusters.labels_ != -1)[0]+1  # Find the indices of elements in the 'clusters.labels_' array that are not labeled as noise (-1), increment each index by 1, and assign the resulting array to areasInd
    
        if len(areasInd) == 0:  # Check if the length of areasInd is 0
            return None  # Return None if areasInd is an empty array
    
        clusters_labels = clusters.labels_  # Assign the labels generated by DBSCAN to clusters_labels
    
        return map_url, final, areasInd, clusters_labels  # Return the variables map_url, final, areasInd, and clusters_labels as the result of the function
    