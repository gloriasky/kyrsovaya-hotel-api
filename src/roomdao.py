from src.db_config import mysql_db
from bson import ObjectId


def add_room(room: dict):
    mycursor = mysql_db.cursor()

    sql = f"INSERT INTO rooms (roomNumber, capacity, price, status) " \
          f"VALUES (%s, %s, %s, %s)"
    values = (room['roomNumber'], room['capacity'], room['price'], room['status'])
    mycursor.execute(sql, values)

    mysql_db.commit()

    print(mycursor.rowcount, "record inserted.")
    mycursor.close()


def get_all_rooms():
    mycursor = mysql_db.cursor()

    mycursor.execute("SELECT * FROM rooms")

    rooms = mycursor.fetchall()
    result: list = []
    for room in rooms:
        _dict = {
            '_id': room[0],
            'roomNumber': room[1],
            'capacity': room[2],
            'price': room[3],
            'status': room[4]
        }
        result.append(_dict)
    mycursor.close()
    return result


def get_room_info(_id: str):
    mycursor = mysql_db.cursor()

    mycursor.execute(f"SELECT * FROM rooms WHERE _id = {_id}")

    room = mycursor.fetchall()[0]
    _dict = {
        '_id': room[0],
        'roomNumber': room[1],
        'capacity': room[2],
        'price': room[3],
        'status': room[4]
    }
    mycursor.close()
    return _dict


def update_room(_id: str, room):
    old_room = get_room_info(_id)
    for key in room:
        if room[key] != old_room[key]:
            print(key)
            print(room[key])
            mycursor = mysql_db.cursor()

            sql = f"UPDATE rooms SET {key} = {room[key]} WHERE _id = {_id}"

            mycursor.execute(sql)

            mysql_db.commit()

            print(mycursor.rowcount, "record(s) affected")
            mycursor.close()


def delete_room(_id: str):
    mycursor = mysql_db.cursor()

    sql = f"DELETE FROM rooms WHERE _id = {_id}"

    mycursor.execute(sql)

    mysql_db.commit()

    print(mycursor.rowcount, "record(s) deleted")
    mycursor.close()




