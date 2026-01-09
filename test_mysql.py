import pymysql

print("Starting MySQL test")

db = pymysql.connect(
    host="localhost",
    user="root",
    password="Deekshamale@123",
    database="atm_db"
)

print("MySQL Connected Successfully")
db.close()