import dbAPI
import datetime
from pageclass import Worksheet


def recommend(worksheet_uid, n=100, c_code="IL", l_code="he"):
    worksheet = Worksheet(worksheet_uid=worksheet_uid, c_code=c_code, l_code=l_code)
    worksheet.build_page()
    rec = worksheet.get_rec(n)
    return rec