from src.db_config import mysql_db, init_db
from werkzeug.security import generate_password_hash, check_password_hash


def find_employee(login: str):
    mycursor = mysql_db.cursor(buffered=True)

    mycursor.execute(f"SELECT * FROM employees WHERE email = '{login}'")

    user = mycursor.fetchall()[0]
    _dict = {
        '_id': user[0],
        'firstName': user[1],
        'lastName': user[2],
        'position': user[3],
        'phone': user[4],
        'permission': user[5],
        'email': user[6]
    }
    mycursor.close()
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
    result = {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'position']}
    return result


def validate_password(login, password):
    user = find_employee(login)
    sql_query = 'select employees.email, employees_passwords.password_hash ' \
                'from employees_passwords ' \
                'inner join employees ' \
                'on employees._id = employees_passwords._id ' \
                f'where employees.email = "{login}"'
    mycursor = mysql_db.cursor(buffered=True)

    mycursor.execute(sql_query)

    user['pswd'] = mycursor.fetchall()[0][1]
    mycursor.close()

    if not user:
        raise Exception('User %s not found' % login)
    elif not check_password_hash(user['pswd'], password):
        raise Exception('Incorrect password')
    return user


def add_employee(employee: dict):

    if find_employee(employee['login']):
        raise Exception('User %s already exists' % employee['login'])

    mycursor = mysql_db.cursor(buffered=True)

    sql = "INSERT INTO employees (firstName, lastName, position, phone, permission, email)" \
          "VALUES (%s, %s, %s, %s, %s,%s)"
    values = (employee['firstName'], employee['lastName'], employee['position',
              employee['phone'], employee['permission'], employee['email']])
    mycursor.execute(sql, values)

    mysql_db.commit()

    print(mycursor.rowcount, "record inserted.")