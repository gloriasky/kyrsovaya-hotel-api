from src.roomdao import get_all_rooms, add_room, update_room, get_room_info, delete_room
from src.servicedao import get_all_services, add_service, update_service, get_service_info, delete_service


class Hotel ():

    def get_rooms(self):
        return get_all_rooms()

    def add_room(self, room: dict):
        add_room(room)

    def get_room(self, _id: str):
        return get_room_info(_id)

    def update_room(self, _id: str, room: dict):
        update_room(_id, room)

    def delete_room(self, _id: str):
        delete_room(_id)

    def get_services(self, filter: str):
        return get_all_services(filter)

    def add_service(self, service: dict):
        add_service(service)

    def get_service(self, _id: str):
        return get_service_info(_id)

    def update_service(self, _id: str, service: dict):
        update_service(_id, service)

    def delete_service(self, _id: str):
        delete_service(_id)


hotel = Hotel()
