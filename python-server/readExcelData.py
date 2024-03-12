import pymysql
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv("/Users/dorperetz/MathCenterRecommendationEngine/python-server/dbenv.env")

# Set the database credentials
HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
USER = os.environ.get("MYSQL_USER")
PASSWORD = os.environ.get("PASSWORD")
DATABASE = os.environ.get("DATABASE")

# Connect to the database
connection = pymysql.connect(
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)

# Create a cursor object
cursor = connection.cursor()

# Execute a SQL query
# cursor.execute("DROP TABLE topics;")
# cursor.execute("DROP TABLE user_downloads;")
# cursor.execute("DROP TABLE worksheet_grades;")
# cursor.execute("DROP TABLE user_interactive_sets;")
# connection.commit()

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

cursor.execute("""CREATE TABLE IF NOT EXISTS worksheet_grades(
    country_code VARCHAR(5),
    language_code VARCHAR(5),
    page_uid VARCHAR(255),
    min_grade VARCHAR(20),
    max_grade VARCHAR(20)
    );""")

cursor.execute("""CREATE TABLE IF NOT EXISTS user_interactive_sets(
    user_uid VARCHAR(255),
    worksheet_template_uid VARCHAR(255),
    language_code VARCHAR(5),
    country_code VARCHAR(5),
    started_at VARCHAR(255)
    );""")
# Fetch the results
connection.commit()

# df = pd.read_csv("/Users/nivdavidian/Downloads/BGU Project data 28.2.24 - User worksheets download.csv")

# i=0
# step = 5000
# t = True
# while(t):
#     if i==(len(df["language_code"])+1):
#         t = False
#     tps = [tuple(x) for x in df.iloc[i:(i+step)].to_numpy()]
#     cursor.executemany("INSERT INTO user_downloads (language_code, country_code, downloads) VALUES (%s, %s, %s)", tps)
#     i = min((i+step), (len(df)+1))
    
# connection.commit()

cursor.execute("SELECT COUNT(*) FROM user_downloads")
res = cursor.fetchall()
print(res)
# df = pd.DataFrame(res, columns=["user_uid", "country_code", "language_code", "downloads"])

# print(df["dowloads"])



# Close the cursor and connection
cursor.close()
connection.close()


