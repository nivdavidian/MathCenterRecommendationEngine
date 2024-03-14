import datetime
import sql_pool
import pandas as pd

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

cursor.execute("""CREATE TABLE IF NOT EXISTS worksheet_titles(
    uid VARCHAR(255),
    language_code VARCHAR(5),
    title VARCHAR(255),
    PRIMARY KEY (uid, language_code)
    );""")

connection.commit()

# df = pd.read_excel("/Users/nivdavidian/Downloads/Worksheet titles.xlsx", sheet_name='Sheet1')

# i=0
# step = 5000
# t = True
# while(t):
#     if i==(len(df["language_code"])+1):
#         t = False
#     tps = [tuple(x) for x in df.iloc[i:(i+step)].to_numpy()]
#     cursor.executemany("INSERT INTO worksheet_titles (uid, language_code, title) VALUES (%s, %s, %s)", tps)
#     i = min((i+step), (len(df)+1))
    
# connection.commit()

# cursor.execute("CREATE FULLTEXT INDEX idx_name ON worksheet_titles(title);")

# sql = """SELECT *
# FROM information_schema.statistics
# WHERE table_schema = 'mathCenterDB' -- Replace with your database name
# AND table_name = 'worksheet_titles'
# AND index_type = 'FULLTEXT';"""

# cursor.execute(sql)
# print(cursor.fetchall())

# connection.commit()

cursor.close()
sql_pool.release_connection(connection)

def get_page_topics_by_uid(pages_uid):
    sql = "SELECT * FROM topics WHERE worksheet_uid IN (%s)"
    place_holders = ", ".join(f"\'{uid}\'"for uid in pages_uid)
    sql = sql % place_holders
    
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(sql)
    res = cursor.fetchall()
    
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_pages_by_topics(topics):
    sql = "SELECT * FROM topics WHERE topic IN (%s)"
    place_holders = ", ".join(topics)
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
    cursor.execute("SELECT page_uid, min_grade, max_grade FROM worksheet_grades WHERE country_code = %s AND language_code = %s", (c_code, l_code))
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

def get_worksheets_page(language, country, page=1):
    per_page = 100  # Number of worksheets per page
    
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    
    
    offset = (page - 1) * per_page  # Calculate offset based on page number
    cursor.execute("""SELECT uid, title
                   FROM worksheet_titles JOIN worksheet_grades
                   ON worksheet_titles.uid = worksheet_grades.page_uid AND worksheet_titles.language_code = worksheet_grades.language_code
                   WHERE worksheet_titles.language_code = (%s) AND worksheet_grades.country_code = (%s) LIMIT %s OFFSET %s""", (language, country, per_page, offset))
    
    res = cursor.fetchall()
    cursor.close()
    sql_pool.release_connection(conn)
    
    return res

def get_page(search_string, l_code="he"):
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT uid, title FROM worksheet_titles
                   WHERE uid = (%s) AND language_code = (%s)
                   """, (search_string, l_code))
    
    res = cursor.fetchall()
    if res == None:
        res = []
    
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_recommendations_for_worksheet(worksheet_uid, l_code, c_code):
    df = pd.read_parquet(f"./top_200_by_country_files/top_200_{l_code}-{c_code}.parquet")
    df.index = df["worksheet_uid"]
    
    res = df.loc[worksheet_uid, "top_10"]
    return res

def get_pages(worksheet_uids, l_code="he"):
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT uid, title FROM worksheet_titles WHERE uid IN (%s) AND language_code = "
    place_holders = ",".join(f"\'{uid}\'"for uid in worksheet_uids)
    sql = sql % place_holders
    sql = sql + "(%s)"
    cursor.execute(sql, (l_code,))
    
    res = cursor.fetchall()
    if res == None:
        res = []
    
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_recommend_search(term, l_code, c_code):
    if term == '':
        return []
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        sql = """SELECT uid, title 
        FROM worksheet_titles
        WHERE MATCH(title) AGAINST (%s IN NATURAL LANGUAGE MODE) 
        AND language_code = %s 
        LIMIT 100;
        """
        cursor.execute(sql, (term, l_code))
        
        res = cursor.fetchall()
        if res == None or len(res) == 0:
            return []
        
        sql = "SELECT page_uid FROM worksheet_grades WHERE language_code = %s AND country_code = %s AND page_uid "
        sql += "IN (%s)" % ", ".join(map(lambda x: f"\'{x[0]}\'", res))
        cursor.execute(sql, (l_code, c_code,))
        uids = [x[0] for x in cursor.fetchall()]
        
        filtered = filter(lambda x: x[0] in uids, res)
        
        return filtered
    except Exception as e:
        print(e)
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)
        
def get_distinct_cl_codes():
    conn = sql_pool.get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT country_code, language_code FROM worksheet_grades GROUP BY country_code, language_code;"
    cursor.execute(sql)
    
    res = cursor.fetchall()
    print(len(res))
    if res == None:
        res = []
    
    cursor.close()
    sql_pool.release_connection(conn)
    return res

def get_file_df(path):
    df = pd.read_parquet(path)
    return df

def get_interactive_by_clcodes(c_code, l_code):
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM user_interactive_sets WHERE country_code = %s AND language_code = %s"
        cursor.execute(sql, (c_code, l_code))
        
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)



# t = datetime.datetime.now()
# get_worksheets_page("he", "IL")
# print(datetime.datetime.now()-t)
# sql_pool.close_conncections()