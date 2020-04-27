import string, random

from src.db_config import guests_table, admins_table, mysql_db
from werkzeug.security import generate_password_hash, check_password_hash


def lowercase_login(func):
    def wrapper(*args, **kwargs):
        args = list(args)
        args[0] = args[0].lower()
        args = tuple(args)
        return func(*args, **kwargs)

    return wrapper


@lowercase_login
def new(login, password=None, **kwargs):
    login = login.lower()

    password = password or generate_password(kwargs.get('permission', []))

    if find_employee(login):
        raise Exception('User %s already exists' % login)

    user = {
        'login': login,
        'email': login,
        'pswd': generate_password_hash(password)
    }
    user = {**kwargs, **user}

    if 'position' in user:
        mycursor = mysql_db.cursor(buffered=True)

        sql = f"INSERT INTO employees (firstName, lastName, position, phone, permission, email)" \
              f"VALUES (%s, %s, %s, %s, %s,%s)"
        values = (
        user['firstName'], user['lastName'], user['position', user['phone'], user['permission'], user['email']])
        mycursor.execute(sql, values)

        mysql_db.commit()

        print(mycursor.rowcount, "record inserted.")
    else:
        mycursor = mysql_db.cursor(buffered=True)

        sql = f"INSERT INTO guests (firstName, lastName, phone, email)" \
              f"VALUES (%s, %s, %s, %s)"
        values = (user['firstName'], user['lastName'], user['phone'], user['email'])
        mycursor.execute(sql, values)

        mysql_db.commit()

        print(mycursor.rowcount, "record inserted.")
    print(f'User %s with password {password} was created' % login)
    return login, password


def new_superadmin(login, password=None):
    return new(login, password, permissions=[PERMISSION_SUPERADMIN], firstName='Admin', lastName='Digatex')


def generate_password(permissions):
    size = random.randint(12, 16) if len(permissions) > 0 else random.randint(8, 12)

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


@lowercase_login
def find_employee(login, reset_password=False):
    mycursor = mysql_db.cursor(buffered=True)

    mycursor.execute(f"SELECT * FROM employees WHERE email = '{login}'")

    user = mycursor.fetchall()[0]
    print(user)
    _dict = {
        '_id': user[0],
        'firstName': user[1],
        'lastName': user[2],
        'position': user[3],
        'phone': user[4],
        'permission': user[5],
        'email': login
    }
    mycursor.close()
    return _dict


def find_admins():
    users = guests_table.find({'permissions': PERMISSION_ADMIN})
    emails = []
    for user in users:
        emails.append(user.get('email'))
    return emails


@lowercase_login
def validate_employee(login, password):
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

    print(generate_password_hash(password))

    if not user:
        raise Exception('User %s not found' % login)
    elif not check_password_hash(user['pswd'], password):
        raise Exception('Incorrect password')
    return user


@lowercase_login
def validate_permission(login, permission):
    user = find_employee(login)
    if not user:
        raise Exception('User %s not found' % login)
    elif permission != user.get('permission'):
        raise Exception('No permissions')


@lowercase_login
def set_password(login, new_password=None):
    if new_password is None:
        user = find(login, True)
        new_password = generate_password(user.get('permissions', []))
    guests_table.update_one({'login': login}, {"$set": {'pswd': generate_password_hash(new_password)}}, upsert=False)
    print('Password for user %s was changed to %s' % (login, new_password))
    return new_password


@lowercase_login
def remove(login):
    guests_table.delete_one({'login': login})
    print('User %s was removed' % login)


def user_view(user):
    result = {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone']}
    return result


def get_all():
    users = guests_table.find()
    result = []
    for user in users:
        result.append(
            {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'company', 'permissions']})
    return result
