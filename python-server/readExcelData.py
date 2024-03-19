import pandas as pd
import sql_pool

conn = sql_pool.get_connection()
cursor = conn.cursor()

def drop_tables(**kwargs):
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        for arg, b in kwargs.items():
            if b:
                try:
                    cursor.execute("DROP TABLE %s;", (arg,))
                except Exception as e:
                    e.add_note(f"arg={arg},b={b} DROP TABLE {arg} not executed")
                    raise(e)
        conn.commit()
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def create_tables_if_not_exist():
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
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
            
        conn.commit()
    except Exception as e:
        e.add_note("Exception in create tables if not exist")
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)
        
def add_data_from_csv(path):
    try:
        df = pd.read_csv(path)
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        i=0
        step = 5000
        t = True
        while(t):
            if i==(df.index.size+1):
                t = False
            tps = [tuple(x) for x in df.iloc[i:(i+step)].to_numpy()]
            cursor.executemany("INSERT INTO user_downloads (country_code, language_code, downloads) VALUES (%s, %s, %s)", tps)
            i = min((i+step), (len(df)+1))

        conn.commit()
    except Exception as e:
        e.add_note(f"Add data from csv: {path} Failed")
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)


