import datetime
import sql_pool
import pandas as pd
import numpy as np


def get_worksheet_info(uids, c_code, l_code):
    place_holders = ", ".join(list(map(lambda _: "%s", uids)))
    sql = f"""SELECT topics.worksheet_uid, topics.topic, worksheet_grades.min_grade, worksheet_grades.max_grade, worksheet_titles.title FROM 
    topics
    JOIN
    worksheet_grades ON topics.worksheet_uid = worksheet_grades.page_uid
    JOIN
    worksheet_titles ON worksheet_titles.uid = worksheet_grades.page_uid AND worksheet_titles.language_code = worksheet_grades.language_code
    WHERE worksheet_grades.country_code = %s AND worksheet_grades.language_code = %s AND topics.worksheet_uid IN ({place_holders})
    """
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql, (c_code, l_code)+tuple(uids))
        
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)
        
def get_page_topics_by_uid(pages_uid):
    try:
        sql = "SELECT * FROM topics WHERE worksheet_uid IN (%s)"
        place_holders = ", ".join(f"\'{uid}\'"for uid in pages_uid)
        sql = sql % place_holders
        
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql)
        res = cursor.fetchall()
        
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_pages_by_topics(topics):
    try:
        sql = "SELECT * FROM topics WHERE topic IN (%s)"
        place_holders = ", ".join(topics)
        sql = sql % place_holders
        
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql, tuple(topics))
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)
        
def get_all_user_downloads():
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_downloads")
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_all_pages_topics():
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topics")
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_all_worksheet_grades():
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM worksheet_grades")
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_worksheet_grades_by_uids(worksheets, c_code, l_code):
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        qm = ",".join(np.full(len(worksheets), "%s"))
        cursor.execute(f"SELECT page_uid, min_grade, max_grade FROM worksheet_grades WHERE country_code = %s AND language_code = %s AND page_uid IN ({qm})", (c_code, l_code)+tuple(worksheets))
        res = cursor.fetchall()
        return res
    except Exception as e:
        print(e)
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_worksheet_grades_by_country_lang(c_code, l_code):
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT page_uid, min_grade, max_grade FROM worksheet_grades WHERE country_code = %s AND language_code = %s", (c_code, l_code))
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_distinct_country_lang():
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT country_code, language_code FROM worksheet_grades")
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_worksheets_page(language, country, page=1):
    try:
        per_page = 100  # Number of worksheets per page
        
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        
        offset = (page - 1) * per_page  # Calculate offset based on page number
        cursor.execute("""SELECT uid, title
                    FROM worksheet_titles JOIN worksheet_grades
                    ON worksheet_titles.uid = worksheet_grades.page_uid AND worksheet_titles.language_code = worksheet_grades.language_code
                    WHERE worksheet_titles.language_code = (%s) AND worksheet_grades.country_code = (%s) LIMIT %s OFFSET %s""", (language, country, per_page, offset))
        
        res = cursor.fetchall()
        
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_page(search_string, l_code="he"):
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT uid, title FROM worksheet_titles
                    WHERE uid = (%s) AND language_code = (%s)
                    """, (search_string, l_code))
        
        res = cursor.fetchall()
        if res == None:
            res = []
        
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_recommendations_for_worksheet(worksheet_uid, l_code, c_code):
    df = pd.read_parquet(f"./top_by_country_files/{l_code}-{c_code}.parquet")
    df.index = df["worksheet_uid"]
    
    res = df.loc[worksheet_uid, "top_10"]
    return res

def get_pages(worksheet_uids, l_code="he"):
    try:
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
        
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

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
        cursor.execute(sql, (f"\'{term}\'", l_code))
        res = cursor.fetchall()
        if res == None or len(res) == 0:
            return []
        
        sql = "SELECT page_uid FROM worksheet_grades WHERE language_code = %s AND country_code = %s AND page_uid "
        sql += "IN (%s)" % ", ".join(["%s" for _ in res])
        tp = tuple([x[0] for x in res])
        cursor.execute(sql, (l_code, c_code)+tp)
        uids = [x[0] for x in cursor.fetchall()]
        filtered = list(filter(lambda x: x[0] in uids, res))
        
        return filtered
    except Exception as e:
        print(e)
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)
        
def get_distinct_cl_codes():
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT country_code, language_code FROM worksheet_grades GROUP BY country_code, language_code;"
        cursor.execute(sql)
        
        res = cursor.fetchall()
        if res == None:
            res = []
        
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)

def get_file_df(path):
    df = pd.read_parquet(path)
    return df

def get_interactive_by_clcodes(c_code, l_code):
    try:
        conn = sql_pool.get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM user_interactive_sets WHERE language_code = %s"
        cursor.execute(sql, (l_code,))
        
        res = cursor.fetchall()
        return res
    except Exception as e:
        raise e
    finally:
        cursor.close()
        sql_pool.release_connection(conn)
