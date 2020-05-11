from src.db_config import init_db
from src import bookings
from bson import ObjectId


def add_room(room: dict):
    db = init_db()
    mycursor = db.cursor()

    sql = f"INSERT INTO rooms (roomNumber, capacity, price, status) " \
          f"VALUES (%s, %s, %s, %s)"
    values = (room['roomNumber'], room['capacity'], room['price'], room['status'])
    mycursor.execute(sql, values)

    db.commit()

    print(mycursor.rowcount, "record inserted.")
    mycursor.close()
    db.close()


def get_all_rooms():
    db = init_db()
    mycursor = db.cursor()

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
    db.close()
    return result


def get_room_info(_id: str):
    db = init_db()
    mycursor = db.cursor()

    mycursor.execute(f"SELECT * FROM rooms WHERE _id = {int(_id)}")

    room = mycursor.fetchall()[0]
    _dict = {
        '_id': room[0],
        'roomNumber': room[1],
        'capacity': room[2],
        'price': room[3],
        'status': room[4]
    }
    mycursor.close()
    db.close()
    return _dict


def update_room(_id: str, room):
    db = init_db()
    old_room = get_room_info(_id)
    for key in room:
        if room[key] != old_room[key]:
            mycursor = db.cursor()

            sql = f"UPDATE rooms SET {key} = '{room[key]}' WHERE _id = {_id}"

            mycursor.execute(sql)

            db.commit()

            print(mycursor.rowcount, "record(s) affected")
            mycursor.close()
    db.close()


def delete_room(_id: str):
    db = init_db()
    mycursor = db.cursor()

    sql = f"DELETE FROM rooms WHERE _id = {_id}"

    mycursor.execute(sql)

    db.commit()

    print(mycursor.rowcount, "record(s) deleted")
    mycursor.close()
    db.close()


def get_available_rooms(capacity: int, date_from, date_to):
    db = init_db()
    mycursor = db.cursor()

    mycursor.execute(f"SELECT * FROM rooms WHERE capacity = {capacity} AND status = 'Available'")

    rooms = mycursor.fetchall()
    result: list = []
    booked = bookings.get_booked_rooms(date_from, date_to)
    for room in rooms:
        if room[0] not in booked:
            _dict = {
                '_id': room[0],
                'roomNumber': room[1],
                'capacity': room[2],
                'price': room[3],
                'status': room[4]
            }
            result.append(_dict)
    mycursor.close()
    db.close()
    return result



