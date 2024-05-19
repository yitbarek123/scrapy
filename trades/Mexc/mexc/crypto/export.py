import csv
import mysql.connector

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'new_user',
    'password': 'password',
    'database': 'mexc',
}

# SQL query to retrieve data
query = "SELECT * FROM BTCUSDT"

# Output CSV file path
output_file_path = 'file.csv'

try:
    # Connect to MySQL
    connection = mysql.connector.connect(**db_config)

    # Create a cursor
    cursor = connection.cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch all the rows
    rows = cursor.fetchall()

    # Write data to CSV file
    with open(output_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write header
        header = [i[0] for i in cursor.description]
        csv_writer.writerow(header)

        # Write data
        csv_writer.writerows(rows)

    print(f'Data exported to {output_file_path}')

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close cursor and connection
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
