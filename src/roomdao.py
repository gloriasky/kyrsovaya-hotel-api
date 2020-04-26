from src.db_config import rooms_table


def add_room(room: dict):
    rooms_table.insert_one(room)


def get_all_rooms():
    rooms = list(rooms_table.find())
    for room in rooms:
        room['_id'] = str(room['_id'])
    return rooms



