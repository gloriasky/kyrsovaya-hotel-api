from pymongo import MongoClient
import mysql.connector

from src.constants import DB

client = MongoClient(DB)
db = client["hotel"]
guests_table = db["guests"]
rooms_table = db["rooms"]
admins_table = db["admins"]


mysql_db = mysql.connector.connect(
              host="127.0.0.1",
              user="root",
              passwd="root",
              auth_plugin='mysql_native_password',
              database="kursovaya-hotel"
              )


def init_db():
    return mysql.connector.connect(
              host="127.0.0.1",
              user="root",
              passwd="root",
              auth_plugin='mysql_native_password',
              database="kursovaya-hotel"
              )
