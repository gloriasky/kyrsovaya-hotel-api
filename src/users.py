import string, random

from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from src.constants import DB


client = MongoClient(DB)
db = client["hotel"]
table = db["guests"]


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

    password = password or generate_password(kwargs.get('permissions', []))

    if find(login):
        raise Exception('User %s already exists' % login)

    user = {
        'login': login,
        'email': login,
        'pswd': generate_password_hash(password)
    }
    user = {**kwargs, **user}

    table.insert_one(user)
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
def find(login, reset_password=False):
    users = table.find({"login": login})

    count = users.count()
    if count == 1:
        return users[0]
    elif count > 0:
        raise Exception('More than one user %s exist' % login)
    elif reset_password and count == 0:
        raise Exception('No such a user!')


def find_admins():
    users = table.find({'permissions': PERMISSION_ADMIN})
    emails = []
    for user in users:
        emails.append(user.get('email'))
    return emails


@lowercase_login
def validate(login, password):
    user = find(login)
    if not user:
        raise Exception('User %s not found' % login)
    elif not check_password_hash(user['pswd'], password):
        raise Exception('Incorrect password')
    return user


def field_beautify(field):
    if field == 'firstName':
        return 'first name'
    elif field == 'lastName':
        return 'last name'
    else:
        return field


def permissions_beautify(permissions):
    if permissions is None:
        return 'Regular user'
    elif len(permissions) == 0:
        return 'Regular user'
    else:
        perm = []
        if 'operator' in permissions:
            perm.append('Nominated Contact Person')
        if 'admin' in permissions:
            perm.append('System Administrator from Operator')
        if 'view' in permissions:
            perm.append('Read only')
        if 'superadmin' in permissions:
            perm.append('Super Administrator')
        return ', '.join(perm)


@lowercase_login
def update(login, field, value=None):
    user = find(login)
    if not user:
        raise Exception('User %s not found' % login)
    if field not in FIELDS_TO_UPDATE:
        raise Exception('Unsupported field. Use one of these: %s.' % ', '.join(FIELDS_TO_UPDATE))

    old_value = user.get(field)

    if field == 'permissions' and value is not None:
        if value == '':
            value = []
        else:
            value = re.split('\s*,\s*', value)

    table.update_one({'login': login}, {"$set": {field: value}}, upsert=False)

    print('Field %s was updated from %s to %s for user %s' % (field, old_value, value, login))

    if field == 'permissions':
        return {'field': field_beautify(field), 'old_value': permissions_beautify(old_value), 'new_value': permissions_beautify(value)}
    else:
        return {'field': field_beautify(field), 'old_value': old_value, 'new_value': value}


@lowercase_login
def validate_permission(login, permission):
    user = find(login)
    if not user:
        raise Exception('User %s not found' % login)
    elif permission not in user.get('permissions', []):
        raise Exception('No permissions')


@lowercase_login
def set_password(login, new_password=None):
    if new_password is None:
        user = find(login, True)
        new_password = generate_password(user.get('permissions', []))
    table.update_one({'login': login}, {"$set": {'pswd': generate_password_hash(new_password)}}, upsert=False)
    print('Password for user %s was changed to %s' % (login, new_password))
    return new_password


@lowercase_login
def remove(login):
    table.delete_one({'login': login})
    print('User %s was removed' % login)


def get_company_operators(company):
    users = table.find({'company': company, 'permissions': PERMISSION_OPERATOR})
    result = []
    for user in users:
        result.append(
            {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'company']})
    return result


def user_view(user):
    result = {key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone']}
    return result


def get_all():
    users = table.find()
    result = []
    for user in users:
        result.append({key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'company', 'permissions']})
    return result


def get_from_company(company):
    users = table.find({'company': company})
    result = []
    for user in users:
        result.append({key: user.get(key) for key in ['email', 'firstName', 'lastName', 'phone', 'company', 'permissions']})
    return result


def get_users_from_company(company):
    users = table.find({'company': company})
    result = []
    for user in users:
        result.append(user.get('email'))
    return result


def update_full(user):
    old_user = find(user['email'])
    updated = []
    for key in user:
        if key not in old_user:
            if key == 'permissions':
                updated.append(update(user['email'], key, ','.join(user[key])))
            else:
                updated.append(update(user['email'], key, user[key]))
        elif old_user[key] != user[key]:
            if key == 'permissions':
                updated.append(update(user['email'], key, ','.join(user[key])))
            else:
                updated.append(update(user['email'], key, user[key]))
    return updated

