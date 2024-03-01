import pymysql
import datetime
import sql_pool
# Set the database credentials
host = 'database-1.cxs6kmykemnz.eu-north-1.rds.amazonaws.com'
port = 3306
user = 'admin'
password = 'jStDcRULtS9CcYh'
database = 'mathCenterDB'

# Connect to the database
connection = sql_pool.get_connection()

# Create a cursor object
cursor = connection.cursor()

# Execute a SQL query
# cursor.execute("DROP TABLE topics;")
# cursor.execute("DROP TABLE downloads;")
# cursor.execute("DROP TABLE worksheet_grades;")
cursor.execute("""CREATE TABLE IF NOT EXISTS topics(
    worksheet_uid VARCHAR(255),
    topic VARCHAR(255),
    PRIMARY KEY (worksheet_uid, topic)
    );""")

cursor.execute("""CREATE TABLE IF NOT EXISTS user_downloads(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(5),
    language_code VARCHAR(5),
    downloads TEXT
    );""")

# cursor.execute("""CREATE TABLE IF NOT EXISTS other_user_downloads(
#     user_id INT AUTO_INCREMENT PRIMARY KEY,
#     country_code VARCHAR(5),
#     language_code VARCHAR(5),
#     page_uid VARCHAR
#     );""")

cursor.execute("""CREATE TABLE IF NOT EXISTS worksheet_grades(
    country_code VARCHAR(5),
    language_code VARCHAR(5),
    page_uid VARCHAR(255),
    min_grade VARCHAR(20),
    max_grade VARCHAR(20)
    );""")

cursor.close()
sql_pool.release_connection(connection)

def get_page_topics_by_uid(pages_uid):
    sql = "SELECT * FROM topics WHERE worksheet_uid IN (%s)"
    place_holders = ", ".join(["%s"]*len(pages_uid))
    sql = sql % place_holders
    
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(sql, tuple(pages_uid))
    res = cursor.fetchall()
    
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_pages_by_topics(topics):
    sql = "SELECT * FROM topics WHERE topic IN (%s)"
    place_holders = ", ".join(["%s"]*len(topics))
    sql = sql % place_holders
    
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(sql, tuple(topics))
    res = cursor.fetchall()
    
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_all_user_downloads():
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_downloads")
    res = cursor.fetchall()
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_all_pages_topics():
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics")
    res = cursor.fetchall()
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_all_worksheet_grades():
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM worksheet_grades")
    res = cursor.fetchall()
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_worksheet_grades_by_country_lang(c_code, l_code):
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT page_uid FROM worksheet_grades WHERE country_code = (%s) AND language_code = (%s)", (c_code, l_code))
    res = cursor.fetchall()
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_distinct_country_lang():
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT country_code, language_code FROM worksheet_grades")
    res = cursor.fetchall()
    cursor.close()
    sql_pool.release_connection(conn)
    return res
    

# t = datetime.datetime.now()
# print(get_page_topics_by_uid(["0038d295", "002fa1e4", "7b9d14c7"]))
# print(datetime.datetime.now()-t)

# connection.close()