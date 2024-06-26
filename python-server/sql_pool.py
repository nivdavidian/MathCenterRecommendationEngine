import pymysql
import datetime
import threading
import time
import os
import queue
from dotenv import load_dotenv
from pymysql.err import OperationalError

load_dotenv("/Users/nivdavidian/MathCenterRecommendationEngine/python-server/dbenv.env")

# Set the database credentials
HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
USER = os.environ.get("MYSQL_USER")
PASSWORD = os.environ.get("PASSWORD")
DATABASE = os.environ.get("DATABASE")


lock = threading.Lock()

MAX_SIZE = 50
overflow = 50
conn_queue = queue.Queue(maxsize=MAX_SIZE)
SLEEP_TIME = 0.1

def create_connection():
    return pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)

def get_connection():
    global lock
    global conn_queue
    global overflow
    while True:
        if conn_queue.empty() and overflow <= 0:
            time.sleep(SLEEP_TIME)
            continue
        conn = None
        create_conn = False
        with lock:
            if conn_queue.empty() and overflow <= 0:
                time.sleep(SLEEP_TIME)
                continue
            elif not conn_queue.empty():
                conn = conn_queue.get_nowait()
            else:
                overflow -= 1
                create_conn = True
                
        if create_conn:
            conn = create_connection()
            
        if conn is None:
            continue
        
        conn = check_conn(conn)
        return conn          

def release_connection(conn):
    global lock
    global conn_queue
    global overflow
    
    with lock:
        if conn_queue.full():
            overflow += 1
            conn.close()
        else:
            conn_queue.put_nowait(conn)
            
    return


def replace_conn_with_new_conn(conn):
    global lock
    
    conn.close()
    return create_connection()
        
    

def close_conncections():
    global lock
    global conn_queue
    global overflow
    
    with lock:
        while not conn_queue.empty():
            conn_queue.get_nowait().close()
    return

def check_conn(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
    except OperationalError:
        conn = create_connection()
    return conn