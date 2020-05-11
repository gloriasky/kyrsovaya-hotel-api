from datetime import datetime
import random
import string

from src.db_config import init_db
from werkzeug.security import generate_password_hash, check_password_hash


def find_employee(login: str):
    db = init_db()
    mycursor = db.cursor(buffered=True)

    mycursor.execute(f"SELECT * FROM employees WHERE email = '{login}'")

    user = mycursor.fetchall()
    if not user:
        return False
    user = user[0]
    _dict = {
        '_id': user[0],
        'firstName': user[1],
        'lastName': user[2],
        'position': user[3],
        'phone': user[4],
        'permission': user[5],
        'email': user[6],
        'dateOfBirth': str(user[7].strftime("%Y-%m-%d"))
    }
    mycursor.close()
    db.close()
    return _dict


def validate_permission(login, permission):
    sql_query = 'select employees.email, employees.permission ' \
                'from employees ' \
                f'where employees.email = "{login}"'
    db = init_db()
    mycursor = db.cursor(buffered=True)

    mycursor.execute(sql_query)

    _permisison = mycursor.fetchall()[0][1]
    mycursor.close()
    db.close()
    if _permisison != permission:
        raise Exception('No permissions')


def user_view(user):
    result = {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'position', 'dateOfBirth']}
    return result


def validate_password(login, password):
    user = find_employee(login)
    db = init_db()
    sql_query = 'select employees.email, employees_passwords.password_hash ' \
                'from employees_passwords ' \
                'inner join employees ' \
                'on employees._id = employees_passwords._id ' \
                f'where employees.email = "{login}"'
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


def add_employee(employee: dict):

    if find_employee(employee['email']):
        raise Exception('User %s already exists' % employee['email'])

    db = init_db()
    mycursor = db.cursor(buffered=True)

    sql = "INSERT INTO employees (firstName, lastName, position, phone, permission, email, dateOfBirth)" \
          "VALUES (%s, %s, %s, %s, %s,%s, %s)"
    values = (employee['firstName'], employee['lastName'], employee['position'],
              employee['phone'], employee['permission'], employee['email'], employee['dateOfBirth'])
    mycursor.execute(sql, values)
    _id = mycursor.lastrowid

    db.commit()

    print(mycursor.rowcount, "record inserted.")

    db.close()

    if employee['createPassword']:
        save_password(_id)


def create_password():
    size = random.randint(8, 12)

    letters = string.ascii_uppercase + string.ascii_lowercase
    digits = string.digits
    special = '!@#$%&*_'

    # one digit and one special
    chars = [random.choice(digits), random.choice(special)]

    # random characters
    for _ in range(size - 4):
        chars.append(random.choice(letters + digits))

    # shuffle
    random.shuffle(chars)

    # add letter in first and last positions
    chars = [random.choice(letters)] + chars + [random.choice(letters)]

    return ''.join(chars)


def get_all_employees():
    db = init_db()
    sql_query = 'select employees._id, employees.email, employees.firstName, employees.lastName, ' \
                'employees.phone, employees.position, employees.dateOfBirth, employees_passwords.password_hash ' \
                'from employees_passwords ' \
                'right join employees ' \
                'on employees._id = employees_passwords.employee_id '
    mycursor = db.cursor(buffered=True)

    mycursor.execute(sql_query)

    employees = mycursor.fetchall()
    result: list = []
    for employee in employees:
        print(employee)
        _dict = {
            '_id': employee[0],
            'email': employee[1],
            'firstName': employee[2],
            'lastName': employee[3],
            'phone': employee[4],
            'position': employee[5],
            'dateOfBirth': employee[6].strftime("%Y-%m-%d"),
            'hasAccess': 'Yes' if employee[7] else 'No'
        }
        result.append(_dict)
    mycursor.close()
    db.close()
    return result


def get_employee(_id):
    db = init_db()
    mycursor = db.cursor()

    mycursor.execute(f"SELECT * FROM employees WHERE _id = {_id}")

    employee = mycursor.fetchall()[0]
    _dict = {
        '_id': employee[0],
        'email': employee[6],
        'firstName': employee[1],
        'lastName': employee[2],
        'phone': employee[4],
        'position': employee[3],
        'permission': employee[5],
        'dateOfBirth': str(employee[7].strftime("%Y-%m-%d"))
    }
    mycursor.close()
    db.close()
    return _dict


def get_password(_id):
    db = init_db()
    mycursor = db.cursor()

    mycursor.execute(f"SELECT * FROM employees_passwords WHERE employee_id = {_id}")

    employee = mycursor.fetchall()
    db.close()
    if len(employee) > 0:
        return True


def save_password(_id):
    password = create_password()
    hash = generate_password_hash(password)
    db = init_db()
    mycursor = db.cursor(buffered=True)

    sql = "INSERT INTO employees_passwords (employee_id, password_hash)" \
          "VALUES (%s, %s)"
    values = (_id, hash)
    mycursor.execute(sql, values)

    db.commit()

    print(password)

    print(mycursor.rowcount, "record inserted.")

    mycursor.close()
    db.close()


def update_password(_id):
    password = create_password()
    hash = generate_password_hash(password)
    db = init_db()
    mycursor = db.cursor(buffered=True)

    sql = f"UPDATE employees_passwords SET password_hash = '{hash}' WHERE employee_id = {_id}"
    mycursor.execute(sql)

    db.commit()

    print(password)

    print(mycursor.rowcount, "record inserted.")


def update_employee(_id: str, employee: dict):
    old_employee = get_employee(_id)
    print(employee)
    db = init_db()
    for key in employee:
        if key != 'createPassword' and employee[key] != old_employee[key]:
            mycursor = db.cursor()

            sql = f"UPDATE employees SET {key} = '{employee[key]}' WHERE _id = {_id}"

            mycursor.execute(sql)

            db.commit()

            print(mycursor.rowcount, "record(s) affected")
            mycursor.close()
    db.close()
    if employee['createPassword']:
        if get_password(_id):
            update_password(_id)
        else:
            save_password(_id)


def delete_employee(_id: str):
    db = init_db()
    mycursor = db.cursor()

    sql = f"DELETE FROM employees WHERE _id = {_id}"

    mycursor.execute(sql)

    db.commit()

    print(mycursor.rowcount, "record(s) deleted")
    mycursor.close()
