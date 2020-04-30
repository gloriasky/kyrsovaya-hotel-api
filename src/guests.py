import random
import string

from src.db_config import mysql_db, init_db
from werkzeug.security import generate_password_hash, check_password_hash


def find_guest(login: str):
    mycursor = mysql_db.cursor(buffered=True)

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
    return _dict


def user_view(user):
    result = {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'numOfArrivals']}
    return result


def validate_password(login, password):
    user = find_guest(login)
    sql_query = 'select guests.email, guests_passwords.password_hash ' \
                'from guests_passwords ' \
                'inner join guests ' \
                'on guests._id = guests_passwords._id ' \
                f'where guests.email = "{login}"'
    mycursor = mysql_db.cursor(buffered=True)

    mycursor.execute(sql_query)

    user['pswd'] = mycursor.fetchall()[0][1]
    mycursor.close()

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

    mycursor = mysql_db.cursor(buffered=True)

    sql = "INSERT INTO guests (firstName, lastName, phone, email)" \
          "VALUES (%s, %s, %s, %s)"
    values = (guest['firstName'], guest['lastName'],
              guest['phone'], guest['email'])
    mycursor.execute(sql, values)
    _id = mycursor.lastrowid

    mysql_db.commit()

    print(mycursor.rowcount, "record inserted.")
    save_password(_id, guest['password'])


def get_all_guests():
    sql_query = 'select guests._id, guests.email, guests.firstName, guests.lastName, guests.phone, guests.numOfArrivals ' \
                'from guests '
    mycursor = mysql_db.cursor(buffered=True)

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
    return result


def get_guest(_id):
    mycursor = mysql_db.cursor()

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
    return _dict


def get_password(_id):
    mycursor = mysql_db.cursor()

    mycursor.execute(f"SELECT * FROM guests_passwords WHERE guest_id = {_id}")

    guest = mycursor.fetchall()
    if len(guest) > 0:
        return True


def save_password(_id, password):
    hash = generate_password_hash(password)
    mycursor = mysql_db.cursor(buffered=True)

    sql = "INSERT INTO guests_passwords (guest_id, password_hash)" \
          "VALUES (%s, %s)"
    values = (_id, hash)
    mycursor.execute(sql, values)

    mysql_db.commit()

    print(password)

    print(mycursor.rowcount, "record inserted.")


def update_password(_id, password):
    hash = generate_password_hash(password)
    mycursor = mysql_db.cursor(buffered=True)

    sql = f"UPDATE guests_passwords SET password_hash = '{hash}' WHERE guest_id = {_id}"
    mycursor.execute(sql)

    mysql_db.commit()

    print(password)

    print(mycursor.rowcount, "record inserted.")


def update_guest(_id: str, guest: dict):
    old_guest = get_guest(_id)
    for key in guest:
        if guest[key] != old_guest[key]:
            mycursor = mysql_db.cursor()

            sql = f"UPDATE guests SET {key} = '{guest[key]}' WHERE _id = {_id}"

            mycursor.execute(sql)

            mysql_db.commit()

            print(mycursor.rowcount, "record(s) affected")
            mycursor.close()


def delete_guest(_id: str):
    mycursor = mysql_db.cursor()

    sql = f"DELETE FROM guests WHERE _id = {_id}"

    mycursor.execute(sql)

    mysql_db.commit()

    print(mycursor.rowcount, "record(s) deleted")
    mycursor.close()
