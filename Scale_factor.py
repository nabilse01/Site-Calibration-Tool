# Import the necessary modules to connect to a database, read configuration files, and work with data
import psycopg2  # module to connect to PostgreSQL databases


def get_scale_factor(floor_id, venue_id, DB_IP, DB_User, DB_PW, DB_name, DB_port):
    DB_IP = DB_IP  # IP address of the database
    DB_User = DB_User  # username to login to the database
    DB_PW = DB_PW  # password to login to the database
    DB_name = DB_name
    DB_port = DB_port

    try:
        # Establishes a connection to the database specified using psycopg2 module
        global conn
        conn = psycopg2.connect(
            user=DB_User,     # Database username
            password=DB_PW,   # Database password
            host=DB_IP,       # Database IP address
            port=DB_port,
            database=DB_name  # Name of the database being accessed
        )

        # Create a cursor object to execute SQL commands on this connection
        cursor = conn.cursor()

        # Construct the SQL command to retrieve the scale factor from given venue_id and floor_id
        query = f"SELECT scale_factor FROM penguin.tblfloors where venue_id={venue_id} and id = {floor_id}  "

        # Execute the query and fetch the first row of the result
        cursor.execute(query)
        result = cursor.fetchone()[0]

        # Return the scale factor result
        return result

    except (Exception, psycopg2.Error) as error:
        print(error)   # Print any errors raised during execution of the code
