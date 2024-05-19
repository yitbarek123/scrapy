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
            PRIMARY KEY (amount, price, time)
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
                price VARCHAR(255),
                amount VARCHAR(255),
                total VARCHAR(255),
                time VARCHAR(255),
                tradetype VARCHAR(255),
                PRIMARY KEY (time)
            )
            """
            # Execute the table creation query
            self.cursor.execute(create_table_query)
            # Commit the transaction
            self.connection.commit()
        except mysql.connector.Error as err:
            # Handle MySQL errors
            print(f"MySQL error: {err}")

    def hm_to_timestamp(self, hours, minutes, ct):
        # Calculate the total seconds from the provided hours and minutes
        total_seconds = hours * 3600 + minutes * 60

        # Get the current time in seconds since the epoch
        current_time_seconds = time.time()

        # Subtract the total seconds to get the desired timestamp
        timestamp_unix = int(current_time_seconds - total_seconds)

        return timestamp_unix

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
            table_name=adapter.get("pair")+"_booking"
            self.create_table(table_name)
            print("######################")
            print("######################")
            print(table_name)
            #print(data)
            print("######################")
            print("######################")
            print("######################")

            #bulk_data=data
            bulk_data=[]
            current_time = datetime.now()
            ct=time.time()
            for d in data:
                try:
                    if len(d)>4:
                        bulk_data.append(d)
                except:
                    pass
            
            if len(bulk_data)>0:
                columns = ['price', 'tradetype','amount', 'time']
                columns = ['price','amount','total','time','tradetype']

                query = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in range(len(columns))])})"

                values = [value for item in bulk_data for value in item]
                v = values
                print("######################")
                print("########nfdjs##############")
                print(table_name)
                print(values)
                print("######################")
                print("######################")
                print("######################")            
                self.cursor.executemany(query, [values[i:i+len(columns)] for i in range(0, len(values), len(columns))])
                #self.connection.commit()
                print("Bulk data inserted successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")