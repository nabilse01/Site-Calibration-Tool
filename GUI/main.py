import time
import configparser
import requests
import json
import tkinter as tk
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from configparser import RawConfigParser
import os
from tkinter import ttk, Radiobutton, IntVar, filedialog,messagebox
import tkinter.messagebox as messagebox
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import signal
import urllib.request
from PIL import Image


def restart_program():
    """Restarts the current program, with file objects and descriptors cleanup."""
    python = sys.executable
    os.execl(python, python, python, *sys.argv)


if not os.path.exists('config.properties'):
    # create the config file with default values
    with open('config.properties', 'w') as f:
        f.write('[database]\n'
                'ip = 192.168.2.31\n'
                'user = test\n'
                'password = Penguineerstest\n'
                'name = PenIQ_Demo\n'
                'port = 5432\n\n'
                '[PE]\n'
                'url = https://sec.penguinin.com:9090/saad_pe/\n'
                '[Server]\n'
                'url = http://192.168.2.250\n'
                )

# Continue with your next instructions here...


config = RawConfigParser()
config.read('config.properties')
DB_IP = config.get('database', 'ip')
DB_User = config.get('database', 'user')
DB_PW = config.get('database', 'password')
DB_name = config.get('database', 'name')
DB_port = config.get('database', 'port')
PE_Url = config.get('PE', 'url')
Server_Url = config.get('Server', 'url')
url = PE_Url + 'PEService.svc/Initialize'


headers = {'Content-Type': 'application/json'}

# Create a GUI window using tkinter with a title of "CDF"
root = tk.Tk()
root.title('CDF')

# Create a cursor object to manipulate data in a database connection called conn
# # rows_venues
json_data = {
    'DB_IP': DB_IP,
    'DB_PW': DB_PW,
    'DB_User': DB_User,
    'DB_name': DB_name,
    'DB_port': DB_port,
    'PE_Url': PE_Url,
    'Server_Url': Server_Url,
}
try:
    rows_venues = requests.post(
        f'{Server_Url}/rows_venues', headers=headers, data=json.dumps(json_data), timeout=None)
    try:
        rows_venues = rows_venues.json()
        venue_names = ["Select Venue"]
        for row in rows_venues:
            venue_names.append(row[1])
    except:
        venue_names = ["Select Venue"]
        var = tk.StringVar(root)
        var.set(venue_names[0])
        # Create a list of floor names starting with the string "Select Floor"
        Floor_names = ["Select Floor"]
        floor_var = tk.StringVar(root)
        messagebox.showerror('Invalid IP',
                               f'The specified IP address is invalid: {DB_IP} or The Database  {DB_name} is not exist or mistyped or the Port Number {DB_port} is Wrong ')
        messagebox.showerror('Error',
                               f'Check the Settings and Try Again ')
except:
    messagebox.showerror('Error',
                         f'Cannot connect to the server {Server_Url},  ')
    venue_names = ["Select Venue"]

    # Set the variable var to the first element of the venue_names list as the default option
    var = tk.StringVar(root)
    var.set(venue_names[0])

    # Create a list of floor names starting with the string "Select Floor"
    Floor_names = ["Select Floor"]
    floor_var = tk.StringVar(root)
    venue_names = ["Select Venue"]
    messagebox.showerror('Error',
                           f'Check the Settings and Try Again ')
    # Set the variable floor_var to the first element of the Floor_names list as the default option


    # Set the variable var to the first element of the venue_names list as the default option



# Store the venue names in a list called venue_names, starting with the string "Select Venue"

# Set the variable var to the first element of the venue_names list as the default option
var = tk.StringVar(root)
var.set(venue_names[0])

# Create a list of floor names starting with the string "Select Floor"
Floor_names = ["Select Floor"]
floor_var = tk.StringVar(root)

# Set the variable floor_var to the first element of the Floor_names list as the default option
floor_var.set(Floor_names[0])


# Define a function restart_program() which will be used to restart the program
# Needed python and os modules

# Define a function select_venue(var) which will be used to choose a venue and get its data
def select_venue(var):
    global floor_dropdown

    # Get the id and name of the selected venue by executing an SQL SELECT query
    # query = f"SELECT id,venue_name FROM penguin.tblvenues WHERE venue_name = '{var}'"
    # cursor.execute(query)
    json_data = {
        'DB_IP': DB_IP,
        'DB_PW': DB_PW,
        'DB_User': DB_User,
        'DB_name': DB_name,
        'DB_port': DB_port,
        'PE_Url': PE_Url,
        'Server_Url': Server_Url,
        'venue_name': var
    }
    rows_venues_0 = requests.post(
        f'{Server_Url}/rows_venues_0', headers=headers, data=json.dumps(json_data), timeout=None)
    rows_venues_0 = rows_venues_0.json()
    # If the result is not None, then the selected venue exist in the database
    if rows_venues_0 is not None:
        # Destroy any previously existing floor dropdown menu
        floor_dropdown.destroy()
        # Set the global variables venue_id and venue_name to match the values attained by the query.
        # Get all floor names for the selected venue
        global venue_id, venue_name

        venue_id, venue_name = rows_venues_0[0]

        json_data = {
            'DB_IP': DB_IP,
            'DB_PW': DB_PW,
            'DB_User': DB_User,
            'DB_name': DB_name,
            'DB_port': DB_port,
            'PE_Url': PE_Url,
            'Server_Url': Server_Url,
            'venue_id': venue_id
        }

        rows_floors = requests.post(
            f'{Server_Url}/rows_floors', headers=headers, data=json.dumps(json_data), timeout=None)
        rows_floors = rows_floors.json()

        # Create a list of floor names starting with the string "Select Floor"
        global selected_floor_id
        selected_floor_id = None
        Floor_names = ["Select Floor"]

        # Append each floor name to the Floor_names list and create a (floor_name, floor_id) couple which will be used later
        for row in rows_floors:
            Floor_names.append(row[1])

        # Store the list of (floor_name, floor_id) tuples in a list called floor_names_and_ids
        floor_names_and_ids = [(row[1], row[0]) for row in rows_floors]

        # Set the default value for the variable floor_var to be the first item in the list Floor_names
        floor_var.set(Floor_names[0])

        # Create a drop-down selection widget called floor_dropdown with the variable floor_var and containing all elements of the list Floor_names
        floor_dropdown = tk.OptionMenu(root, floor_var, *Floor_names)

        # Set its grid position
        floor_dropdown.grid(row=1, column=0)

        # Define a function select_floor(*args) that captures the user-selected floor and sets the global variable selected_floor_id to the corresponding floor_id
        def select_floor(*args):
            global selected_floor_id, selected_floor_name
            selected_floor_name = floor_var.get()

            for name, floorid in floor_names_and_ids:
                if name == selected_floor_name:
                    selected_floor_id = floorid

        # Create a button to select the floor and get its data
        # When floor_var is modified (i.e. the user selects a value), call the function select_floor()
        floor_var.trace("w", select_floor)

    else:
        selected_floor_id = None
        venue_id = None

    # Call the select_floor() function at the end of select_venue() to have the content displayed.
    select_floor()

    # Check if conn exists before closing cursor and connection


# Save the configuration values to the config file
def save_config():
    # Get the path of config file and Open the config file for reading
    config_file = os.path.join(os.getcwd(), 'config.properties')
    config = configparser.ConfigParser()
    config.read(config_file)

    # Get the new values from respective text boxes in UI
    new_ip = ip_textbox.get()  # New IP value
    new_db_name = db_name_textbox.get()  # New Database Name value
    new_db_port = db_port_textbox.get()
    new_Pe = Pe_textbox.get()  # New PE URL value
    new_Server = Server_textbox.get()  # New Server URL value
    # Write/Update the above new values in config file
    # set function represents section, key and the updated value is passed
    config.set('database', 'ip', new_ip)
    config.set('database', 'name', new_db_name)
    config.set('database', 'port', new_db_port)
    config.set('PE', 'url', new_Pe)
    config.set('Server', 'url', new_Server)

    # Save the changes by writing them into the config file object
    with open(config_file, 'w') as f:
        config.write(f)

    # Update message and restart the program
    message_label.config(text="Config saved successfully!")
    restart_program()


def save_file_fp():
    # Open file dialog to choose save location
    file_path = filedialog.asksaveasfilename(initialfile=f"linesToBeRepeated_fp for {venue_name} floor{selected_floor_name}.txt",
                                             defaultextension=".txt",
                                             title="Save File",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as output:
            output.write(str(linesToBeRepeated_fp))


def main_saveFiles_fp(linesToBeRepeated):
    # Replace it with your actual data
    venue_name = "Venue"
    selected_floor_name = "Floor"
    global root4
    root4 = tk.Tk()
    root4.title("Save File")

    # Create a label to display information
    info_label = tk.Label(
        root4, text=f"This will save '{linesToBeRepeated}' to a file.")
    info_label.pack()

    # Create save button
    save_button = tk.Button(
        root4, text="Save", command=lambda: save_file_fp(linesToBeRepeated))
    save_button.pack(pady=10)

    # Create cancel button
    cancel_button = tk.Button(root4, text="Cancel", command=root4.quit)
    cancel_button.pack()

    root4.mainloop()

# Insert/Update the given parameters by executing SQL queries on the database connection


def save_file_sig():
    # Open file dialog to choose save location
    file_path = filedialog.asksaveasfilename(initialfile=f"SigsToBeRepeated for {venue_name} floor{selected_floor_name}.txt",
                                             defaultextension=".txt",
                                             title="Save File",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as output:
            output.write(str(linesToBeRepeated_sig))
        return


def main_saveFiles_sig(linesToBeRepeated):
    # Replace it with your actual data
    venue_name = "Venue"
    selected_floor_name = "Floor"
    global root2
    root2 = tk.Tk()
    root2.title("Save File")

    # Create a label to display information
    info_label = tk.Label(
        root2, text=f"This will save '{linesToBeRepeated}' to a file.")
    info_label.pack()

    # Create save button
    save_button = tk.Button(
        root2, text="Save", command=lambda: save_file_sig(linesToBeRepeated))
    save_button.pack(pady=10)

    # Create cancel button
    cancel_button = tk.Button(root2, text="Cancel", command=root2.quit)
    cancel_button.pack()
    root2.mainloop()
    return


def Draw_CDF(Diff, min_sum_key, venue_name, selected_floor_name, diff_maxerorr, diff_value_95th):
    # sort the difference data from smallest to largest
    sorted_data = np.sort(Diff)
    # compute the cumulative distribution function (CDF) values corresponding to each data point in the sorted data
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    # plot the CDF using the sorted data as x and CDF values as y, and label it with min_sum_key
    plt.plot(sorted_data, yvals, label=f"{min_sum_key}")
    plt.title(
        f"max error : {diff_maxerorr:.2f}\nvalue at 95th percentile: {diff_value_95th:.2f}")
    # get the current figure instance
    fig1 = plt.gcf()
    # set the title of the figure with the venue_id and floor_id
    # show the legend of the figure
    plt.legend()
    # display the figure
    plt.show()
    # save the figure as a PNG file with the name based on the venue_id and floor_id
    fig1.savefig(
        f'Venue_Name_{venue_name}  Floor_Name_{selected_floor_name}' + '.png', dpi=100)
    return

# Define a function named calculate with no input parameter, which will use global variables to fetch values from previous operation
# status_label = tk.Label(root, text="API is not working yet", fg="red")
# status_label.grid(row=4, column=0)


def my_progress_bar():
    global root1
    root1 = tk.Tk()
    root1.title("Status")
    root1.geometry("300x100")

    # label to show the status
    # create progress bar
    global progress_bar
    progress_bar = ttk.Progressbar(
        root1, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.pack(pady=20)
    progress_bar.start()

    # update progress bar value

    # set status message
    status_label = tk.Label(root1, text="processing...",
                            font=("Arial Bold", 12))
    status_label.pack()

    root1.mainloop()


def calculate():

    global venue_id
    global selected_floor_id
    if venue_id != None and selected_floor_id != None:
        # Reassigning the same values for the venueID and floorID for new calculation.
        venue_id = venue_id

        floor_id = selected_floor_id
        # Assign values to Monte Carlo iteration, maximum error and 95 percent error; Get values from UI inputs or assign default value (10, 10, 5) in case of non-numeric inputs
        montecarloIter = int(E3.get()) if str(E3.get()).isnumeric() else 10
        max_error = int(E4.get()) if str(E4.get()).isnumeric() else 10
        ninety_five_percent_error = int(
            E5.get()) if str(E5.get()).isnumeric() else 5

    # Create a dictionary object named json_data, which includes venueID, floorID, Monte Carlo iteration, maximum error, and 95% error as key-value pairs.

    json_data = {
        "venue_id": venue_id,
        "floor_id": floor_id,
        "montecarloIter": montecarloIter,
        "max_error": max_error,
        "ninety_five_percent_error": ninety_five_percent_error,
        'DB_IP': DB_IP,
        'DB_PW': DB_PW,
        'DB_User': DB_User,
        'DB_name': DB_name,
        'DB_port': DB_port,
        'PE_Url': PE_Url,
        'Server_Url': Server_Url
    }

    # Update message label with start message
    def make_api_request():
        response = requests.post(
            f'{Server_Url}/D_O', headers=headers, data=json.dumps(json_data), timeout=None)
        return response

    def CDF():
        json_data = {
            "venue_id": venue_id,
            "floor_id": floor_id,
            "montecarloIter": montecarloIter,
            "max_error": max_error,
            "ninety_five_percent_error": ninety_five_percent_error,
            'DB_IP': DB_IP,
            'DB_PW': DB_PW,
            'DB_User': DB_User,
            'DB_name': DB_name,
            'PE_Url': PE_Url,
            'DB_port': DB_port,
            'Server_Url': Server_Url,
            'Response': 'Yes'
        }
        response = requests.post(
            f'{Server_Url}/CDF', headers=headers, data=json.dumps(json_data), timeout=None)

        res_text = response.json()

        diff_all_str = res_text.get("response", {}).get("DiffAll", "")
        # create a list of float values from space-separated string "diff_all_str".
        diff_all = [float(x) for x in diff_all_str]

        # Get values of minimum difference, maximum error distance, 95th percentile value from JSON response and assign them to available variables.
        diff_min = res_text.get("response", {}).get("min_sum_key", "")
        diff_maxerorr = res_text.get("response", {}).get("max_error_D", "")
        diff_value_at_95th_percentile = res_text.get(
            "response", {}).get("value_at_95th_percentile", "")
        # If calculated maximum error and 95% percentile error less than maximum configuration setting for the same, draw CDF using values computed in step 2, print Minimum key values, and selected floor ID.
        if float(diff_maxerorr) < max_error or float(diff_value_at_95th_percentile) < ninety_five_percent_error:
            Draw_CDF(diff_all, diff_min, venue_name, selected_floor_name, diff_maxerorr,
                     diff_value_at_95th_percentile)
            # insert_min_key(diff_min, floor_id=floor_id)
            json_data = {
                "diff_min": diff_min,
                "floor_id": floor_id,
                'DB_IP': DB_IP,
                'DB_PW': DB_PW,
                'DB_User': DB_User,
                'DB_name': DB_name,
                'PE_Url': PE_Url,
                'Server_Url': Server_Url,
                'Response': 'Yes'
            }
            response = requests.post(f'{Server_Url}/Upload_Keys', headers=headers, data=json.dumps(json_data),
                                     timeout=None)
            root1.withdraw()

        # The following code creates a confirmation window containing a plot with sorted data and y-values.
        # It also defines an action function that saves a figure based on the response to a button ('Yes' or 'No').
        # Finally, it destroys the confirmation window.

        else:
            # Sort the data
            sorted_data = np.sort(diff_all)
            # Create y-values
            yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)

            # Create the confirmation window
            window = tk.Tk()

            # Plot the sorted data and y-values
            fig, ax = plt.subplots()
            ax.plot(sorted_data, yvals, label=f"{diff_min}")
            plt.title(
                f"max error: {diff_maxerorr:.2f}\nvalue at 95th percentile: {diff_value_at_95th_percentile:.2f}")
            plt.legend()

            # Turn the plot into a Tkinter widget
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack()
            plt.close(fig)

            # Define an action function for the buttons

            def action(button):
                if button == 'Yes':
                    # Save the figure
                    fig.savefig(
                        f'Venue_Name  {venue_name} Floor_Name  {selected_floor_name}' + '.png', dpi=100)
                    # Insert the min key based on the floor_id
                    json_data = {
                        "diff_min": diff_min,
                        "floor_id": floor_id,
                        'DB_IP': DB_IP,
                        'DB_PW': DB_PW,
                        'DB_User': DB_User,
                        'DB_name': DB_name,
                        'PE_Url': PE_Url,
                        'Server_Url': Server_Url,
                        'Response': 'Yes'
                    }
                    fig.savefig(
                        f'CDF for Venue_Name_{venue_name}_Floor_Name_{selected_floor_name}.png', dpi=100)
                    response = requests.post(f'{Server_Url}/Upload_Keys', headers=headers, data=json.dumps(json_data),
                                             timeout=None)
                    root1.withdraw()
                elif button == 'Check Design':
                    window.withdraw()
                    Design_Check()
                else:
                    # Save the figure without adding a min key
                    fig.savefig(
                        f'CDF for Venue_Name  {venue_name} Floor_Name  {selected_floor_name}' + '.png', dpi=100)
                    json_data = {
                        "floor_id": floor_id,
                        'DB_IP': DB_IP,
                        'DB_PW': DB_PW,
                        'DB_User': DB_User,
                        'DB_name': DB_name,
                        'DB_port': DB_port,
                    }
                    result = messagebox.askyesno("Warning",
                                                    f"The FingerPrint for {venue_name} floor {selected_floor_name} will be deleted. Are you Sure ? ")
                    if result:
                        response = requests.post(f'{Server_Url}/Delete_FP', headers=headers, data=json.dumps(json_data),
                                                 timeout=None)
                        window.destroy()
                        root1.withdraw()
                    else:
                        pass

            # Creating the 'Yes' button
            # This code creates a tkinter label object, sets its text, color and font size, and adds it to the main window with some padding.
            label = tk.Label(window, text="Do you Approve this CDF ?",
                             fg="blue", font=("Helvetica", 16))
            label.pack(padx=10, pady=10)

            # This code creates a tkinter button object 'Yes', which when clicked calls the action() function with an argument 'Yes'. The button is added to the main window.
            yes_button = tk.Button(
                window, text="Yes", command=lambda: action('Yes'))
            yes_button.pack()

            # This code creates a tkinter button object 'No', which when clicked calls the action() function with an argument 'No'. The button is also added to the main window.
            no_button = tk.Button(
                window, text="No", command=lambda: action('No'))
            no_button.pack()
            Check_Design_button = tk.Button(
                window, text="Check Design", command=lambda: action('Check Design'))
            Check_Design_button.pack()

    def Design_Check():
        json_data = {
            "venue_id": venue_id,
            "floor_id": floor_id,
            'DB_IP': DB_IP,
            'DB_PW': DB_PW,
            'DB_User': DB_User,
            'DB_name': DB_name,
            'DB_port': DB_port,
            "ninety_five_percent_error": ninety_five_percent_error
        }
        response = requests.post(
            f'{Server_Url}/Design', headers=headers, data=json.dumps(json_data), timeout=None)
        res_text = response.json()
        map_url = res_text.get("response", {}).get("map_url", "")
        if len(map_url) != 0:
            map = np.array(Image.open(urllib.request.urlopen(map_url)))
        final = res_text.get("response", {}).get("final", "")
        if final is None:
            root1.withdraw()
            messagebox.showerror(
                '', f'Design for {venue_name} floor {selected_floor_name} is good ')
            return
        final = np.array(final)
        areasInd = res_text.get("response", {}).get("areasInd", "")
        areasInd = np.array(areasInd)
        if len(final) == 0 or len(areasInd) == 0:
            root1.withdraw()
            messagebox.showerror(
                '', f'Design for {venue_name} floor {selected_floor_name} is good ')
            return
        plt.ioff()
        clusters_labels = res_text.get(
            "response", {}).get("clusters_labels", "")
        clusters_labels = np.array(clusters_labels)
        fig, ax3 = plt.subplots()
        ax3.imshow(map)
        ax3.set_title('Highlighted area need more beacon')
        scatter = ax3.scatter(
            final[:, 0], final[:, 1], cmap='viridis', marker='s', s=1)
        fig.savefig(
            f'Area with weak coverage to be repeated  for {venue_name} floor {selected_floor_name}.png', dpi=300, bbox_inches='tight')
        plt.show()
        return

    def plot_Dens_orian():

        map_url_fp = res_text.get("response", {}).get("map_url_fp", "")
        data_sensors_fp = res_text.get(
            "response", {}).get("data_sensors_fp", "")
        probPoints_fp = res_text.get("response", {}).get("probPoints_fp", "")
        if len(map_url_fp) != 0:
            map_image_fp = np.array(Image.open(urllib.request.urlopen(map_url_fp)))
        data_sensors_fp = np.array(data_sensors_fp)
        probPoints_fp = np.array(probPoints_fp)
        stop_fp = res_text.get("response", {}).get("stop_fp", "")
        data_sensors_sig = res_text.get(
            "response", {}).get("data_sensors_sig", "")
        data_sensors_sig = np.array(data_sensors_sig)
        probPoints_sig = res_text.get("response", {}).get("probPoints_sig", "")
        probPoints_sig = np.array(probPoints_sig)
        map_url_sig = res_text.get("response", {}).get("map_url_sig", "")
        if len(map_url_sig) != 0:
            map_image_sig = np.array(Image.open(urllib.request.urlopen(map_url_sig)))
        global linesToBeRepeated_fp
        linesToBeRepeated_fp = res_text.get(
            "response", {}).get("linesToBeRepeated_fp", "")
        linesToBeRepeated_fp = np.array(linesToBeRepeated_fp)
        global linesToBeRepeated_sig
        linesToBeRepeated_sig = res_text.get(
            "response", {}).get("linesToBeRepeated_sig", "")
        linesToBeRepeated_sig = np.array(linesToBeRepeated_sig)
        stop_sig = res_text.get("response", {}).get("stop_sig", "")
        if len(map_url_sig) == 0 and len(map_url_fp) == 0:
            CDF()
            return
        if stop_sig == 'True' and choice == 2:
            messagebox.showerror(
                'Warning', f'Signatures with not enough data and/or collected in a wrong direction were detected . Please repeate these Signatures to Continue')
            window = tk.Tk()
            fig, ax2 = plt.subplots()
            # Subplot for fp_result
            ax2.imshow(map_image_sig)
            ax2.scatter(data_sensors_sig[probPoints_sig == 1, 1],
                       data_sensors_sig[probPoints_sig == 1, 2], marker='+')
            ax2.legend(['Sig Lines to be repeated'])
            ax2.set_title('Sig Lines to be repeated')

            root1.withdraw()
            # cv2.imwrite("full_resolution_map_image.jpg", fig)
            plt.savefig(
                f'Sig Lines to be repeated for {venue_name} floor {selected_floor_name}.png', dpi=300, bbox_inches='tight')
            plt.close(fig)

            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack()

            # Define the action function for the buttons

            def action(button):
                if button == 'Save':
                    window.destroy()
                    # response = requests.post(f'{Server_Url}/CDF', headers=headers, data=json.dumps(json_data), timeout=None)
                else:
                    window.destroy()
                    root1.withdraw()
                    # insert_min_key(diff_min, floor_id=floor_id)

            # Create the 'Yes' button

            yes_button = tk.Button(window, text="Save Signatures",  command=lambda: (
                save_file_sig(), action('Save')))
            yes_button.pack()

            no_button = tk.Button(window, text="Cancel",
                                  command=lambda: action('No'))

            no_button.pack()
            return
        if int(stop_fp) == 2 and choice == 2:
            messagebox.showerror(
                'Error', f'Lines with not enough data and/or collected in a wrong direction were detected . Please repeate these Lines and export the FingerPrint again to Continue')
            window = tk.Tk()
            fig, ax1 = plt.subplots()
            # Subplot for fp_result
            ax1.imshow(map_image_fp)
            ax1.scatter(data_sensors_fp[probPoints_fp == 1, 1],
                        data_sensors_fp[probPoints_fp == 1, 2], marker='+')
            ax1.legend(['Fp Lines to be repeated'])
            ax1.set_title('Fp Lines to be repeated')
            root1.withdraw()
            plt.savefig(
                f'Fp Lines to be repeated for {venue_name} floor {selected_floor_name}.png', dpi=300, bbox_inches='tight')
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack()

            # Define the action function for the buttons

            def action(button):
                if button == 'Yes':
                    window.destroy()
                    root1.withdraw()
                    # response = requests.post(f'{Server_Url}/CDF', headers=headers, data=json.dumps(json_data), timeout=None)
                else:
                    window.destroy()
                    root1.withdraw()
                    # insert_min_key(diff_min, floor_id=floor_id)

            # Create the 'Yes' button

            yes_button = tk.Button(window, text="Saved Lines",  command=lambda: (
                save_file_fp(), action('Yes')))
            yes_button.pack()

            no_button = tk.Button(window, text="Cancel",
                                  command=lambda: action('No'))

            no_button.pack()
            return

        if len(probPoints_sig) == 0:
            pass
        else:
            window1 = tk.Tk()
            fig, ax2 = plt.subplots()
            # Subplot for fp_result
            ax2.imshow(map_image_sig)
            ax2.scatter(data_sensors_sig[probPoints_sig == 1, 1],
                       data_sensors_sig[probPoints_sig == 1, 2], marker='+')
            ax2.legend(['Sig Lines to be repeated'])
            ax2.set_title('Sig Lines to be repeated')

            # cv2.imwrite("full_resolution_map_image.jpg", fig)
            plt.savefig(f'Sig Lines to be repeated for {venue_name} floor {selected_floor_name}.png', dpi=300,
                        bbox_inches='tight')
            plt.close(fig)

            canvas = FigureCanvasTkAgg(fig, master=window1)
            canvas.draw()
            canvas.get_tk_widget().pack()

            # Define the action function for the buttons

            def action(button):
                if button == 'Yes':
                    window1.destroy()
                    # response = requests.post(f'{Server_Url}/CDF', headers=headers, data=json.dumps(json_data), timeout=None)
                else:
                    window1.destroy()
                    # insert_min_key(diff_min, floor_id=floor_id)

            # Create the 'Yes' button

            yes_button = tk.Button(window1, text="Save Signatures", command=lambda: (
                save_file_sig(), action('Yes')))
            yes_button.pack()

            no_button = tk.Button(window1, text="Cancel",
                                  command=lambda: action('No'))

            no_button.pack()
            plt.close()
            window1.wait_window()

        if len(data_sensors_fp) == 0:
            pass
        else:
            window = tk.Tk()
            fig, ax1 = plt.subplots()
            # Subplot for fp_result
            ax1.imshow(map_image_fp)
            ax1.scatter(data_sensors_fp[probPoints_fp == 1, 1],
                        data_sensors_fp[probPoints_fp == 1, 2], marker='+')
            ax1.legend(['Fp Lines to be repeated'])
            ax1.set_title('Fp Lines to be repeated')
            plt.savefig(f'Fp Lines to be repeated for {venue_name} floor {selected_floor_name}.png', dpi=300,
                        bbox_inches='tight')
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack()

            # Define the action function for the buttons

            def action(button):
                if button == 'Yes':
                    window.destroy()
                    CDF()
                elif button == 'Saved and cancle':
                    window.destroy()
                    root1.withdraw()
                elif button == 'Continue Without Save':
                    window.destroy()
                    CDF()
                else:
                    window.destroy()
                    root1.withdraw()
                    # insert_min_key(diff_min, floor_id=floor_id)

            # Create the 'Yes' button

            saved_continue_button = tk.Button(
                window, text="Continue and Save Lines id as text ", command=lambda: (save_file_fp(), action('Yes')))
            saved_continue_button.pack()
            continue_button = tk.Button(window, text="Continue Without Saving",
                                        command=lambda: (action('Continue Without Save')))
            continue_button.pack()
            saved_cancle_button = tk.Button(window, text="Cancle and Save Lines id as text",
                                            command=lambda: (save_file_fp(), action('Saved and cancle')))
            saved_cancle_button.pack()

            no_button = tk.Button(window, text="Cancel",
                                  command=lambda: action('No'))

            no_button.pack()
            plt.close()
        if len(data_sensors_fp) == 0 and len(data_sensors_sig) == 0:
            CDF()
            return

    try:
        response = requests.get(url)
        # Check the status code of the response (200 = OK)
        if response.status_code == 200:
            try:
                api_thread = threading.Thread(target=make_api_request)
                bar_thread = threading.Thread(target=my_progress_bar)
                # start both threads
                # api_thread.start()
                bar_thread.start()

                # wait for both threads to complete before exiting
                res_text = make_api_request().json()
                plot_Dens_orian()

            except Exception as e:
                Check_Fp = requests.post(
                    f'{Server_Url}/Check_Fp', headers=headers, data=json.dumps(json_data), timeout=None)
                Check_Fp = Check_Fp.json()
                if Check_Fp[0][0] == 0:
                    messagebox.showerror(
                        'Error', f'There is no Fingerprint data for this {selected_floor_name} floor')
                    progress_bar.stop()
                    root1.withdraw()
                    pass
                Check_Fp_sensors = requests.post(
                    f'{Server_Url}/Check_Fp_sensors', headers=headers, data=json.dumps(json_data), timeout=None)
                Check_Fp_sensors = Check_Fp_sensors.json()
                if Check_Fp_sensors[0][0] == 0:
                    messagebox.showerror(
                        'Error', f'There is no Fingerprint Sensors data for this {selected_floor_name} floor')
                    progress_bar.stop()
                    root1.withdraw()
                    pass

                Check_Sig = requests.post(
                    f'{Server_Url}/Check_Sig', headers=headers, data=json.dumps(json_data), timeout=None)
                Check_Sig = Check_Sig.json()
                if Check_Sig[0][0] == 0:
                    messagebox.showerror(
                        'Error', f'There is no Signature data for this {selected_floor_name} floor')
                    progress_bar.stop()
                    root1.withdraw()
                    pass
                Check_Sig_sensors = requests.post(
                    f'{Server_Url}/Check_Sig_sensors', headers=headers, data=json.dumps(json_data), timeout=None)
                Check_Sig_sensors = Check_Sig_sensors.json()
                if Check_Sig_sensors[0][0] == 0:
                    messagebox.showerror(
                        'Error', f'There is no Signature Sensors data for this {selected_floor_name} floor')
                    progress_bar.stop()
                    root1.withdraw()
                    pass
            # Extract the "DiffAll" value string from the JSON response and then split into list.

        else:
            messagebox.showerror(
                'PE Url Error ', 'The PE Url is Not Responding . Please Check Your PE Url.')
    except:
        pass


# Use python library Requests to perform an HTTP post request to local host server running on port 5000 by providing header parameters, data as Request body. Get response in JSON format.

def show_choice():
    global choice
    choice = var_2.get()
    if choice == 1:
        pass
    elif choice == 2:
        pass


choice = 2

# Creating a label for the number of repetitions
L3 = tk.Label(root, text='Number of Repetions :', font=40)
# Setting its position in row 2 and column 0 of the grid layout
L3.grid(row=2, column=0)

# Creating an Entry widget for inputting the number of repetitions
E3 = tk.Entry(root, fg='red')
# Setting default value to "10" using the insert() method
E3.insert(tk.END, '10')
# Setting its position in row 2 and column 1 of the grid layout
E3.grid(row=2, column=1)

# Creating a label for the maximum accepted error
L4 = tk.Label(root, text='Max Accepted Error:', font=40)
# Setting its position in row 3 and column 0 of the grid layout
L4.grid(row=3, column=0)

# Creating an Entry widget for inputing the maximum accepted error
E4 = tk.Entry(root, fg='red')
# Setting default value to "10" using the insert() method
E4.insert(tk.END, '10')
# Setting its position in row 3 and column 1 of the grid layout
E4.grid(row=3, column=1)

# Creating a label for the 95 percent error
L5 = tk.Label(root, text='95 percent error:', font=40)
# Setting its position in row 4 and column 0 of the grid layout
L5.grid(row=4, column=0)

# Creating an Entry widget for inputting the 95 percent error
E5 = tk.Entry(root, fg='red')
# Setting default value to "5" using the insert() method
E5.insert(tk.END, '5')
# Setting its position in row 4 and column 1 of the grid layout
E5.grid(row=4, column=1)

# Create a dropdown object with a root window and select a venue from a predefined list
dropdown = tk.OptionMenu(root, var, *venue_names, command=select_venue)
dropdown.grid(row=0, column=0)

# Create another dropdown object to choose a floor
floor_dropdown = tk.OptionMenu(root, floor_var, *Floor_names)
floor_dropdown.grid(row=1, column=0)

# Create a button object for submitting data to a given function

submit_button = tk.Button(root, text="Submit", command=calculate)
submit_button.grid(row=5, column=0)

# Create an output label widget
output_label = tk.Label(root, text="")
output_label.grid(row=7, column=0, columnspan=2)
var_2 = IntVar(value=2)
var_2.set(2)


yes_button = Radiobutton(root, text="Yes", variable=var_2,
                         value=1, command=show_choice)

no_button = Radiobutton(root, text="No", variable=var_2,
                        value=2, command=show_choice)

# Define and create label widgets and text entry fields
ip_label = tk.Label(root, text="IP Database :")
ip_textbox = tk.Entry(root)
ip_textbox.insert(tk.END, DB_IP)
db_name_label = tk.Label(root, text="Database Name:")
db_name_textbox = tk.Entry(root)
db_name_textbox.insert(tk.END, DB_name)
db_port_label = tk.Label(root, text="Database port:")
db_port_textbox = tk.Entry(root)
db_port_textbox.insert(tk.END, DB_port)
Pe_label = tk.Label(root, text="Pe Url :")
Pe_textbox = tk.Entry(root, width=50)
Pe_textbox.insert(tk.END, PE_Url)
Server_label = tk.Label(root, text="Server Url :")
Server_textbox = tk.Entry(root, width=33)
Server_textbox.insert(tk.END, Server_Url)
question_label = tk.Label(root, text="Skip the Density and orientation test ?")


# Create two buttons for saving and canceling changes
message_label = tk.Label(root)
save_button = tk.Button(root, text="Save", command=save_config)
cancel_button = tk.Button(root, text="Exit", command=root.quit)

# Place all the labeling widgets and button objects on their respective row and column values
ip_label.grid(row=6, column=0)
ip_textbox.grid(row=6, column=1)
db_name_label.grid(row=7, column=0)
db_name_textbox.grid(row=7, column=1)
db_port_label.grid(row=8, column=0)
db_port_textbox.grid(row=8, column=1)
Pe_label.grid(row=9, column=0)
Pe_textbox.grid(row=9, column=1)
Server_label.grid(row=10, column=0)
Server_textbox.grid(row=10, column=1)
question_label.grid(row=11, column=0)
yes_button.grid(row=11, column=1)
no_button.grid(row=12, column=1)
message_label.grid(row=14, columnspan=3)
save_button.grid(row=13, column=0)
cancel_button.grid(row=13, column=1)

# Create a list of all labels and text entry widgets to be toggled in "Advanced Options" button
labels = [L3, L4, L5, ip_label, ip_textbox,
          db_name_label, message_label, Pe_label, Server_label, db_port_label, yes_button]
entries = [E3, E4, E5, save_button, cancel_button, db_name_textbox,
           Pe_textbox, Server_textbox, db_port_textbox, question_label, no_button]

# Hide all the labels and text entries added recently by looping through them and calling grid_remove()
for label in labels:
    label.grid_remove()
for entry in entries:
    entry.grid_remove()


# Define a function to toggle the hidden text entry fields on click event of Advanced Options button


def toggle_entries():
    for label in labels:
        if label.winfo_ismapped():  # check if the label widget is already displayed or not
            submit_button = tk.Button(root, text="Submit", command=calculate)
            submit_button.grid(row=5, column=0)
            label.grid_remove()
            entries[labels.index(label)].grid_remove()
        else:
            label.grid()
            entries[labels.index(label)].grid()


def on_closing():
    os.kill(os.getpid(), signal.SIGTERM)
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
# Create another button for changing advanced settings and then add it to the GUI
toggle_button = tk.Button(
    root, text="Advanced Options", command=toggle_entries)
toggle_button.grid(row=14, columnspan=9)
signal.signal(signal.SIGTERM, on_closing)
# Run the root window and GUI interface using mainloop() method.
root.mainloop()
