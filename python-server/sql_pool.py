import pymysql
import datetime
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv("/Users/nivdavidian/MathCenterRecommendationEngine/python-server/dbenv.env")

# Set the database credentials
HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
USER = os.environ.get("MYSQL_USER")
PASSWORD = os.environ.get("PASSWORD")
DATABASE = os.environ.get("DATABASE")

MAX_CONNECTIONS = 1
lock = threading.Lock()

free_connections = [pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE) for _ in range(MAX_CONNECTIONS)]
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
        

