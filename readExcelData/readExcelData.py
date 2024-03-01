import pymysql
import pandas as pd

# Set the database credentials
host = 'database-1.cxs6kmykemnz.eu-north-1.rds.amazonaws.com'
port = 3306
user = 'admin'
password = 'jStDcRULtS9CcYh'
database = 'mathCenterDB'

# Connect to the database
connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

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
# Fetch the results
connection.commit()

cursor.execute("SELECT * FROM user_downloads")
res = cursor.fetchall()
print(len(res))
df = pd.DataFrame(res, columns=["user_uid", "country_code", "language_code", "downloads"])

# print(df["dowloads"])
# df = pd.read_excel("/Users/nivdavidian/Downloads/BGU_Project_data.xlsx", sheet_name='User worksheets download')

# i=0
# step = 5000
# t = True
# while(t):
#     if i==(len(df["language_code"])+1):
#         t = False
#     tps = [tuple(x) for x in df.iloc[i:(i+step)].to_numpy()]
#     cursor.executemany("INSERT INTO user_downloads (country_code, language_code, downloads) VALUES (%s, %s, %s)", tps)
#     i = min((i+step), (len(df)+1))
    
# connection.commit()



# Close the cursor and connection
cursor.close()
connection.close()


