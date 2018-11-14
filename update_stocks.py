import sqlite3
import sys
import os
import pandas as pd
import datetime.datetime

def scrape_kenpom():
    url = "https://kenpom.com"
    columns = [
        "Rk", "Team", "Conf", "W-L",
        "AdjEM", "AdjO", "AdjORnk", "AdjD", "AdjDRnk",
        "AdjT", "AdjTRnk", "Luck", "LunkRnk",
        "SOSAdjEM", "SOSAdjEMRnk", "OppO", "OppORnk",
        "OppD", "OppDRnk", "NCSOSAdjEM", "NCSOSAdjEMRnk"
    ]
    kp_df = pd.read_html(url, header=[0, 1])[0]
    kp_df.columns = columns
    return kp_df

def limit_and_calculate_prices(kp_df):
    major_conf = ["ACC", "Amer", "B10", "B12", "BE", "P12", "SEC", "Conf"]
    mid_majors = kp_df[
        ~kp_df["Conf"].isin(major_conf) &
        ~kp_df["AdjEM"].isnull()
    ].copy()
    mid_majors["AdjEM_num"] = mid_majors["AdjEM"]\
        .apply(lambda x: float(x.replace("+", "")))
    mid_majors["price"] = mid_majors["AdjEM_num"] + \
                          abs(mid_majors["AdjEM_num"].min()) + \
                          0.1
    mid_majors.to_csv("price_csvs/prices_{}".format(datetime.utcnow()), index=None)
    return mid_majors
    
def insert_data(db_path, df):
    conn = sqlite3.connect('app.db')


    for i, r in df.iterrows():
        # print(r["price"], r["name"])
        sql = '''UPDATE stock
                SET price = {}
                WHERE name = "{}"
            '''.format(r["price"], r["Team"])
        # print(sql)
        cur = conn.cursor()
        cur.execute(sql)

    select = '''SELECT * FROM stock WHERE name = "Abilene Christian"'''
    cur = conn.cursor()
    cur.execute(select)
    print(cur.fetchall()[0])
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1]
    kp_df = scrape_kenpom()
    mid_df = limit_and_calculate_prices(kp_df)
    insert_data(db_path, mid_df)