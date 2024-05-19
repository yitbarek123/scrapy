# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
import csv
import json
import mysql.connector
from datetime import datetime, timedelta
import time

class CryptoPipeline:
    def process_item(self, item, spider):
        return item

class MySQLPipeline:
    def __init__(self, db_config):
        self.db_config = db_config
        self.table_name=""
        self.cnt=0
        self.flag=False

    @classmethod
    def from_crawler(cls, crawler):
        return cls(db_config=crawler.settings.getdict('DB_CONFIG'))

    def open_spider(self, spider):
        self.connection = mysql.connector.connect(**self.db_config)
        self.cursor = self.connection.cursor()

        # Create the table with unique constraints on field1, field2, and field3
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transactions (
            amount VARCHAR(255),
            price VARCHAR(255),
            time VARCHAR(255),
            PRIMARY KEY (amount, price, time, tradetype)
        )
        """
        self.cursor.execute(create_table_query)

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def watch_time_to_unix_timestamp(self, hours, minutes, seconds):
        # Create a timedelta object with the provided hours, minutes, and seconds
        watch_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        # Get the current date and time
        current_time = datetime.now()
        # Subtract the watch time from the current time to get the target time
        target_time = current_time - watch_time

        # Convert the target time to a Unix timestamp
        unix_timestamp = int(target_time.timestamp())

        return unix_timestamp
    def create_table(self,table_name):
        try:
            # Define the table creation query with the dynamic table name
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                tradetype VARCHAR(255),
                price VARCHAR(255),
                amount VARCHAR(255),
                time VARCHAR(255),
                PRIMARY KEY (amount, price, tradetype)
            )
            """
            # Execute the table creation query
            self.cursor.execute(create_table_query)
            # Commit the transaction
            self.connection.commit()
        except mysql.connector.Error as err:
            # Handle MySQL errors
            print(f"MySQL error: {err}")

    def watch_time_to_unix_timestamp(self, hours, minutes, seconds):
        # Create a timedelta object with the provided hours, minutes, and seconds
        watch_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        # Get the current date and time
        current_time = datetime.now()
        # Subtract the watch time from the current time to get the target time
        target_time = current_time - watch_time

        # Convert the target time to a Unix timestamp
        unix_timestamp = int(target_time.timestamp())

        return unix_timestamp

    def hm_to_timestamp(self, hours, minutes, ct):
        # Calculate the total seconds from the provided hours and minutes
        total_seconds = hours * 3600 + minutes * 60

        # Get the current time in seconds since the epoch
        current_time_seconds = time.time()

        # Subtract the total seconds to get the desired timestamp
        timestamp_unix = int(current_time_seconds - total_seconds)

        current_datetime = datetime.now()

        # Extract year, month, and day
        current_year = current_datetime.year
        current_month = current_datetime.month
        current_day = str(current_year)+"-"+str(current_month)+"-"+str(current_datetime.day)
        return current_day

    def process_item(self, item, spider):
        #query = (
        #    "INSERT INTO transactions (amount, price, time) "
        #    "VALUES (%s, %s, %s)"
        #)
        #values = (item['field1'], item['field2'], item['field3'])

        #try:
        #    self.cursor.execute(query, values)
        #    self.connection.commit()
        #except mysql.connector.Error as err:
        #    spider.logger.error(f"MySQL error: {err}")
        try:
            print("######################")
            print("######################")
            print("check")
            print("######################")
            print("######################")
            print("######################")
            adapter = ItemAdapter(item)
            data = adapter.get("data")
            table_name=adapter.get("pair")
            self.create_table(table_name)
            print("######################")
            print("######################")
            print(table_name)
            
            print("######################")
            print("######################")
            print("######################")

            #bulk_data=data
            bulk_data=[]
            current_time = datetime.now()
            ct=time.time()
            for d in data:
                t=d[1]
                l="1234"#t.split(":")
                #tm=self.watch_time_to_unix_timestamp(int(l[0]),int(l[1]),int(l[2]),current_time)
                current_time = datetime.now()
                tm=self.hm_to_timestamp(int(l[0]),int(l[1]),ct)
                l=[]
                l.append(d[0])
                l.append(d[1])
                l.append(d[2])
                l.append(d[3])
                l.append(tm)
                bulk_data.append(tuple(l))
            
            if len(bulk_data)>0:
                columns = ['amount', 'price', 'time','tradetype']
                columns = ['tradetype','price','amount','time','todaydate']
                query = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in range(len(columns))])})"

                values = [value for item in bulk_data for value in item]
                v = values            
                print("v1")
                print(values)
                v=values[-5:]
                v1=v[1]
                v2=v[2]
                v3=v[0]
                print("v1")
                conditions = {
                    "amount": v1,
                    "price": v2,
                    "tradetype":v3,
                    "time":v[3],
                    "todaydate":v[4],
                    # Add more columns and values as needed
                }
                print(v)
                print(conditions)
                # Construct the SQL query with a WHERE clause for each condition
                where_conditions = " AND ".join([f"{column} = %s" for column in conditions])
                query2 = f"SELECT * FROM {table_name} WHERE {where_conditions}"

                # Execute the query with the condition values
                try:
                    self.cursor.execute(query2, tuple(conditions.values()))
                    existing_row = self.cursor.fetchall()
                except:
                    self.connection = mysql.connector.connect(**self.db_config)
                    self.cursor = self.connection.cursor()
                    self.cursor.execute(query2, tuple(conditions.values()))
                    existing_row = self.cursor.fetchall()
                # Fetch the result
                # Check if the row exists
                if existing_row:
                    print("######################")
                    print("######################")
                    print("######################")
                    print("The row exists.")
                    # Process the existing row as needed
                    print(existing_row)
                else:
                    print("The row does not exist.")
                    file_path = f'missing_{table_name}_3.txt'

                    # Open the file in append mode ('a')
                    with open(file_path, 'a') as file:
                        # Write each item in the list to a new line in the file
                        file.write(f"{self.cnt} >> {datetime.now()}\n")
                    self.cnt+=1
                # Specify the file path
                file_path = 'outputresult.txt'

                # Open the file in append mode ('a')
                #with open(file_path, 'a') as file:
                #    # Write each item in the list to a new line in the file
                #    file.write(f"{values}\n")

                print(f"List has been appended to {file_path}")
                try:
                    self.cursor.executemany(query, [values[i:i+len(columns)] for i in range(0, len(values), len(columns))])
                except:
                    self.connection = mysql.connector.connect(**self.db_config)
                    self.cursor = self.connection.cursor()
                    self.cursor.executemany(query, [values[i:i+len(columns)] for i in range(0, len(values), len(columns))])
                #self.connection.commit()
                print("Bulk data inserted successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def create_table(self,table_name):
        if self.flag==False:
            try:
                # Define the table creation query with the dynamic table name
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    price VARCHAR(25),
                    tradetype VARCHAR(25),
                    amount VARCHAR(25),
                    time VARCHAR(25),
                    todaydate VARCHAR(25),
                    PRIMARY KEY (price,tradetype,amount,time,todaydate)
                )
                """
                # Execute the table creation query
                self.cursor.execute(create_table_query)
                # Commit the transaction
                self.connection.commit()
                self.flag=True
            except mysql.connector.Error as err:
                # Handle MySQL errors
                self.connection = mysql.connector.connect(**self.db_config)
                self.cursor = self.connection.cursor()
                self.create_table(table_name)
                print(f"MySQL error: {err}")