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

class CoinbasePipeline:

    def __init__(self):
        # Specify the CSV file name
        self.csv_file_path = 'output.csv'
        self.table_name="transactions"
    
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        data = adapter.get("data")
        #with open(os.path.join("data","coinbase.csv"),"a", newline="") as csv_file:
        #    writer = csv.writer(csv_file)
        #    for i in data:
        #        print("yes yes yes yes")
        #        print("yes yes yes yes")
        #        print(float(eval(i)[0]))
        #        print("yes yes yes yes")
        #        print("yes yes yes yes")
        #        l=eval(i)
        #        writer.writerow([l[0],l[1],l[2]])


        return item
    def process_item2(self, item, spider):
        # Check if the CSV file exists; if not, write the header
        if not hasattr(self, 'csv_initialized'):
            with open(self.csv_file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header based on the number of elements in the first list
                csv_writer.writerow(['Value_{}'.format(i + 1) for i in range(len(item[0]))])
            self.csv_initialized = True

        # Append the values of each internal list as a new row in the CSV file
        with open(self.csv_file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(item)

        return item

class MySQLPipeline:
    def __init__(self, db_config):
        self.db_config = db_config
        self.table_name=""

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

            bulk_data=data
            columns = ['price', 'tradetype','amount', 'time']
            query = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in range(len(columns))])})"

            values = [value for item in bulk_data for value in item]
            self.cursor.executemany(query, [values[i:i+len(columns)] for i in range(0, len(values), len(columns))])
            #self.connection.commit()
            print("Bulk data inserted successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        return item

    def create_table(self,table_name):
        try:
            # Define the table creation query with the dynamic table name
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                amount VARCHAR(255),
                price VARCHAR(255),
                time VARCHAR(255),
                tradetype VARCHAR(255),
                PRIMARY KEY (amount, price, time)
            )
            """
            # Execute the table creation query
            self.cursor.execute(create_table_query)
            # Commit the transaction
            self.connection.commit()
        except mysql.connector.Error as err:
            # Handle MySQL errors
            print(f"MySQL error: {err}")
