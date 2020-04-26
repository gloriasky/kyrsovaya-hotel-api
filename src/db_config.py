from pymongo import MongoClient

from src.constants import DB

client = MongoClient(DB)
db = client["hotel"]
guests_table = db["guests"]
rooms_table = db["rooms"]