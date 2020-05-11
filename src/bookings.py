from pymongo import MongoClient, DESCENDING
from src.constants import DB
from src import roomdao, servicedao, guests
from datetime import datetime
from bson import ObjectId

client = MongoClient(DB)
db = client['hotel']
table = db['bookings']


def save_booking(booking: dict):
    booking['status'] = 'Booked'
    table.insert_one(booking)


def get_user_bookings(user_id: int):
    bookings = list(table.find({'guestId': user_id}).sort("to", DESCENDING))
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        booking['room'] = roomdao.get_room_info(booking['roomId'])
        booking['services'] = []
        booking['servicesPrice'] = 0
        if 'servicesIds' in booking:
            for _id in booking['servicesIds']:
                service = servicedao.get_service_info(_id)
                booking['services'].append(service['name'])
                booking['servicesPrice'] += service['price']

            booking['services'] = ', '.join(booking['services'])

    return bookings


def get_all_bookings():
    bookings = list(table.find({}).sort("to", DESCENDING))
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        booking['guestEmail'] = guests.get_guest(booking['guestId'])['email']
        booking['room'] = roomdao.get_room_info(booking['roomId'])
        booking['services'] = []
        booking['servicesPrice'] = 0
        if 'servicesIds' in booking:
            for _id in booking['servicesIds']:
                service = servicedao.get_service_info(_id)
                booking['services'].append(service['name'])
                booking['servicesPrice'] += service['price']

            booking['services'] = ', '.join(booking['services'])
    return bookings


def get_booked_rooms(_from, to):
    bookings = list(table.find({'$and': [{'from': {'$lte': _from}}, {'to': {'$gt': _from}}, {'$or': [{'status': 'Booked'}, {'status': 'Checked In'}]}]}))
    booked = []
    for booking in bookings:
        booked.append(booking['roomId'])
    return booked


def update_booking(booking):
    old_booking = table.find_one({'_id': ObjectId(booking['_id'])})
    print(booking)
    print(old_booking)
    for key in booking:
        if key != '_id' and booking[key] != old_booking[key]:
            table.update_one({'_id': ObjectId(booking['_id'])}, {"$set": {key: booking[key]}}, upsert=False)
            print('Field %s was updated from %s to %s' % (key, old_booking[key], booking[key]))


def get_user_booking(_id):
    booking = table.find_one({'_id': ObjectId(_id)})
    booking['_id'] = str(booking['_id'])
    booking['room'] = roomdao.get_room_info(booking['roomId'])
    booking['services'] = []
    if 'servicesIds' in booking:
        for _id in booking['servicesIds']:
            service = servicedao.get_service_info(_id)
            booking['services'].append(service)
    return booking

