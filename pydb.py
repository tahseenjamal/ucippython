#!/usr/bin/python3

import pymysql

db = pymysql.connect("localhost","root","eves1981","teste" )
cursor = db.cursor()
sql = "SELECT * FROM categories"
try:
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        catid = row[0]
        catname = row[1]
        print (f"catID = {catid}, catName ={catname}")
except:
    print ("Error: unable to fetch data")
db.close()

