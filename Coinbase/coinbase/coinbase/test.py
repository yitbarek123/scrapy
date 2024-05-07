import mysql.connector

# MySQL database connection parameters
db_config = {
    'host': '127.0.0.1',
    'user': 'new_user',
    'password': 'password',
    'database': 'exchange',
}

try:
    # Try to connect to the MySQL database
    connection = mysql.connector.connect(**db_config)

    if connection.is_connected():
        print(f"Connected to MySQL database: {db_config['database']}")
    else:
        print("Failed to connect to MySQL database")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the database connection in the finally block
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("MySQL connection closed")