from pyhive import hive
import pandas as pd
import hive_config
import os, sys


# These are the connection settings for our Hive Database
host = hive_config.host
database = hive_config.database
username = hive_config.username
password = hive_config.password
authentication = hive_config.authentication


# Establishing the connection with the hive database
def sql_conn():
    try:
        connection = hive.connect(host=host,
                                  username=username,
                                  password=password,
                                  authentication=authentication)
        return connection

    except hive.Error as error:
        print("The connection to the hive database failed.", error)

connection = sql_conn()
cursor = connection.cursor()

# This is the query to test if select query is working correctly on the hive database
try:
    select_query = "SELECT * FROM lm4_prod.muse_temp WHERE year = ? and month = ? limit 10"
    cursor.execute(select_query, (year, month))
    result = (cursor.fetchall())
    pdf = pd.DataFrame(data=result)
    print(pdf)

    print(len(result))
    for row in result:
      print(row)
    print("Data has been read from the test table")

except Exception as e:
    print('Error: ', str(e))

# This is the query to test if insert query is working correctly on the hive database
try:
    insert_query  = "INSERT INTO lm4_mu871.pyhive_test (c1,c2) values (?, ?)"
    values = [a, b]
    cursor.execute(insert_query, values)
    cursor.commit()
    print("Data has been inserted test table")

except Exception as e:
    print('Error: ', str(e))
