from src.roomdao import get_all_rooms

class Hotel():

    def get_rooms(self):
        return get_all_rooms()


hotel = Hotel()