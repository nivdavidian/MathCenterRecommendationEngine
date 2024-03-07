import dbAPI
from pageclass import Worksheet


def recommend(worksheet_uid, n=10, c_code="IL", l_code="he"):
    worksheet = Worksheet(worksheet_uid=worksheet_uid, c_code=c_code, l_code=l_code)
    rec = worksheet.get_rec(n)
    return rec