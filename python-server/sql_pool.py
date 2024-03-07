import pymysql
import datetime
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/Users/nivdavidian/MathCenterRecommendationEngine/python-server/dbenv.env")

host="mathcenterinstance.cxs6kmykemnz.eu-north-1.rds.amazonaws.com"
port=3306
user="admin"
password="gencIb-kyqtoj-7cigty"
database="mathCenterDB"

# host = os.getenv("HOST")
# port = int(os.getenv("PORT"))
# user = os.getenv("USER")
# password = os.getenv("PASSWORD")
# database = os.getenv("DATABASE")

# print(host)

MAX_CONNECTIONS = 1
lock = threading.Lock()

free_connections = [pymysql.connect(host=host, port=port, user=user, password=password, database=database) for _ in range(MAX_CONNECTIONS)]
busy_connections = []

def get_connection():
    while True:
        lock.acquire()
        try:
            if len(free_connections) == 0:
               time.sleep(3)
            conn = free_connections.pop()
            busy_connections.append(conn)
            return conn
        finally:
            lock.release()
            

def release_connection(conn):
    while True:
        lock.acquire()
        try:
            busy_connections.remove(conn)
            free_connections.append(conn)
            return
        finally:
            lock.release()
    

def close_conncections():
    free_connections.extend(busy_connections)
    for conn in free_connections:
        conn.close()
        

