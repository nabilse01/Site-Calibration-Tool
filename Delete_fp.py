import psycopg2  # Importing psycopg2 library to work with PostgreSQL

# Define a function called Delete_FP that takes floor_id, DB_IP, DB_User, DB_PW, DB_name, and DB_port as parameters


def Delete_FP(floor_id, DB_IP, DB_User, DB_PW, DB_name, DB_port):
    DB_IP = DB_IP  # IP address of the database
    DB_User = DB_User  # username to login to the database
    DB_PW = DB_PW  # password to login to the database
    DB_name = DB_name  # name of the database
    DB_port = DB_port  # port number of the database

    try:
        global conn  # Declaring 'conn' as a global variable

        # Establish a connection to the PostgreSQL database using the provided credentials
        conn = psycopg2.connect(
            user=DB_User,  # Username for PostgreSQL
            password=DB_PW,  # Password for PostgreSQL
            host=DB_IP,  # Host IP address of the PostgreSQL server
            port=DB_port,  # Port number of the PostgreSQL server
            database=DB_name  # Name of the database to connect to
        )

        cur = conn.cursor()  # Create a cursor object to interact with the database

        # Delete existing entries from penguin.tblfp_rssi_readings table where floor_id matches the given floor_id
        cur.execute(
            "DELETE FROM penguin.tblfp_rssi_readings WHERE floor_id = %s", (floor_id,))

        conn.commit()  # Commit the transaction

    except (Exception, psycopg2.Error) as error:  # Catch any exceptions or errors
        print(error)  # Print the error message if any occurs
