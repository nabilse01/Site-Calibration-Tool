# Import required libraries and read csv file
import psycopg2  # module to connect to PostgreSQL databases
import datetime

# This function takes in an argument that represents venue_id and floor_id


def convert(venue_id, floor_id, DB_IP, DB_User, DB_PW, DB_name, DB_port):
    # Assign values received as arguments to appropriate variables
    DB_IP = DB_IP  # IP address of the database
    DB_User = DB_User  # username to login to the database
    DB_PW = DB_PW  # password to login to the database
    DB_name = DB_name
    DB_port = DB_port

    # Try to establish the connection with the PostgreSQL database using the provided parameters
    try:
        global conn
        conn = psycopg2.connect(
            user=DB_User,           # Username for PostgreSQL
            password=DB_PW,         # Password for PostgreSQL
            host=DB_IP,             # Host IP address of the PostgreSQL server
            port=DB_port,           # Port number of the PostgreSQL server
            database=DB_name        # Name of the database to connect to
        )

        # Create a Cursor object to execute SQL commands on this connection
        cur = conn.cursor()

        # Delete existing entries from penguin.tblfp_rssi_readings and penguin.tblfp_macs table respectively where floor_id matches with the given floor_id
        # Then, insert data into penguin.tblfp_rssi_readings and penguin.tblfp_macs tables by selecting data from penguin.tblfp_data table which matches venue_id and floor_id as provided in array
        now = datetime.datetime.now()
        cur.execute(f"""
            DELETE FROM penguin.tblfp_rssi_readings where floor_id = {floor_id} ;
            DELETE FROM penguin.tblfp_macs where floor_id = {floor_id};
            INSERT INTO penguin.tblfp_rssi_readings (line_id, mac, rssi, ssid, floor_id, x, y, band, active, create_date, last_update, update_status)
                SELECT line_id, major_minor, rssi, uuid, floor_id, x, y, '2', 'True', create_date, '{now}', '1' 
                FROM penguin.tblfp_data 
                WHERE venue_id = {venue_id} AND floor_id = {floor_id};
            INSERT INTO penguin.tblfp_macs (mac, ssid, floor_id, x, y, band, active, create_date)
                SELECT major_minor, uuid, floor_id, x, y, '2', 'True', create_date 
                FROM penguin.tblfp_data 
                WHERE venue_id = {venue_id} AND floor_id = {floor_id};
        """)

        # Commit changes to the database
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        print(error)
