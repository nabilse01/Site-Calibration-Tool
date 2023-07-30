import psycopg2


def insert_min_key(DB_IP, DB_User, DB_PW, DB_name, min_sum_key, floor_id, DB_port):
    # Assigning parameter values to local variables
    DB_IP = DB_IP  # IP address of the database
    DB_User = DB_User  # username to login to the database
    DB_PW = DB_PW  # password to login to the database
    DB_name = DB_name
    DB_port = DB_port

    try:
        global conn
        # Establish a connection to PostgreSQL database using psycopg2 module
        conn = psycopg2.connect(
            user=DB_User,  # Username for postgresql
            password=DB_PW,  # Password for postgresql
            host=DB_IP,  # Host IP address of postgresql server
            port=DB_port,  # Port number of postgresql server
            database=DB_name  # Name of the database to connect to
        )

        # Create a Cursor object to execute SQL commands on this connection
        cursor = conn.cursor()

        # Construct SQL queries to update penguin.tblsystem_settings table with the new values
        sql0 = f"Update penguin.tblsystem_settings set value = {min_sum_key[3]} ,last_update = now()  where parameter_group = 'Position Engine' and settings_type_id = 2 and description = 'BleRSSIcutOff' and reference_id = {floor_id};"
        sql1 = f"Update penguin.tblsystem_settings set value = {min_sum_key[1]} ,last_update = now()where parameter_group = 'Position Engine' and settings_type_id = 2 and description = 'MinParticles' and reference_id = {floor_id};"
        sql2 = f"Update penguin.tblsystem_settings set value = {min_sum_key[0]} ,last_update = now() where parameter_group = 'Position Engine' and settings_type_id = 2 and description = 'MaxParticles' and reference_id = {floor_id};"
        sql3 = f"Update penguin.tblsystem_settings set value = {min_sum_key[2]} ,last_update = now() where parameter_group = 'Position Engine' and settings_type_id = 2 and description = 'StandardDeviation' and reference_id = {floor_id};"

        # Execute the SQL queries
        cursor.execute(sql0)
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.execute(sql3)

        conn.commit()  # Commit the changes to the database

    except (Exception, psycopg2.Error) as error:
        print(error)
