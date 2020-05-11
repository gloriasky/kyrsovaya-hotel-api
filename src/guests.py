import random
import string

from src.db_config import init_db
from werkzeug.security import generate_password_hash, check_password_hash


def find_guest(login: str):
    db = init_db()
    mycursor = db.cursor(buffered=True)

    mycursor.execute(f"SELECT * FROM guests WHERE email = '{login}'")

    user = mycursor.fetchall()
    if not user:
        return False
    user = user[0]
    _dict = {
        '_id': user[0],
        'firstName': user[1],
        'lastName': user[2],
        'phone': user[4],
        'email': user[3],
        'numOfArrivals': user[5]
    }
    mycursor.close()
    db.close()
    return _dict


def user_view(user):
    result = {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'numOfArrivals']}
    return result


def validate_password(login, password):
    db = init_db()
    user = find_guest(login)
    sql_query = 'select guests.email, guests_passwords.password_hash ' \
                'from guests_passwords ' \
                'inner join guests ' \
                'on guests._id = guests_passwords._id ' \
                f'where guests.email = "{login}"'
    mycursor = db.cursor(buffered=True)

    mycursor.execute(sql_query)

    user['pswd'] = mycursor.fetchall()[0][1]
    mycursor.close()
    db.close()

    if not user:
        raise Exception('User %s not found' % login)
    elif not check_password_hash(user['pswd'], password):
        raise Exception('Incorrect password')
    return user


def add_guest(guest: dict):

    if find_guest(guest['email']):
        raise Exception('User %s already exists' % guest['email'])

    if 'phone' not in guest:
        guest['phone'] = None

    db = init_db()
    mycursor = db.cursor(buffered=True)

    sql = "INSERT INTO guests (firstName, lastName, phone, email)" \
          "VALUES (%s, %s, %s, %s)"
    values = (guest['firstName'], guest['lastName'],
              guest['phone'], guest['email'])
    mycursor.execute(sql, values)
    _id = mycursor.lastrowid

    db.commit()

    print(mycursor.rowcount, "record inserted.")
    db.close()
    save_password(_id, guest['password'])


def get_all_guests():
    sql_query = 'select guests._id, guests.email, guests.firstName, guests.lastName, guests.phone, guests.numOfArrivals ' \
                'from guests '
    db = init_db()
    mycursor = db.cursor(buffered=True)

    mycursor.execute(sql_query)

    guests = mycursor.fetchall()
    result: list = []
    for guest in guests:
        _dict = {
            '_id': guest[0],
            'email': guest[1],
            'firstName': guest[2],
            'lastName': guest[3],
            'phone': guest[4],
            'numOfArrivals': guest[5]
        }
        result.append(_dict)
    mycursor.close()
    db.close()
    return result


def get_guest(_id):
    db = init_db()
    mycursor = db.cursor()

    mycursor.execute(f"SELECT * FROM guests WHERE _id = {_id}")

    user = mycursor.fetchall()[0]
    _dict = {
        '_id': user[0],
        'firstName': user[1],
        'lastName': user[2],
        'phone': user[4],
        'email': user[3],
        'numOfArrivals': user[5]
    }
    mycursor.close()
    db.close()
    return _dict


def get_password(_id):
    db = init_db()
    mycursor = db.cursor()

    mycursor.execute(f"SELECT * FROM guests_passwords WHERE guest_id = {_id}")

    guest = mycursor.fetchall()
    db.close()
    if len(guest) > 0:
        return True


def save_password(_id, password):
    hash = generate_password_hash(password)
    db = init_db()
    mycursor = db.cursor(buffered=True)

    sql = "INSERT INTO guests_passwords (guest_id, password_hash)" \
          "VALUES (%s, %s)"
    values = (_id, hash)
    mycursor.execute(sql, values)

    db.commit()

    print(password)

    print(mycursor.rowcount, "record inserted.")
    db.close()


def update_password(_id, password):
    hash = generate_password_hash(password)
    db = init_db()
    mycursor = db.cursor(buffered=True)

    sql = f"UPDATE guests_passwords SET password_hash = '{hash}' WHERE guest_id = {_id}"
    mycursor.execute(sql)

    db.commit()

    print(password)

    print(mycursor.rowcount, "record inserted.")
    db.close()


def update_guest(_id: str, guest: dict):
    old_guest = get_guest(_id)
    db = init_db()
    for key in guest:
        if guest[key] != old_guest[key]:
            mycursor = db.cursor()

            sql = f"UPDATE guests SET {key} = '{guest[key]}' WHERE _id = {_id}"

            mycursor.execute(sql)

            db.commit()

            print(mycursor.rowcount, "record(s) affected")
            mycursor.close()

    db.close()


def delete_guest(_id: str):
    db = init_db()
    mycursor = db.cursor()

    sql = f"DELETE FROM guests WHERE _id = {_id}"

    mycursor.execute(sql)

    db.commit()

    print(mycursor.rowcount, "record(s) deleted")
    mycursor.close()
    db.close()
