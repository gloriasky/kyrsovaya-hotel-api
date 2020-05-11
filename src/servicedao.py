from src.db_config import init_db


def add_service(service: dict):
    db = init_db()
    mycursor = db.cursor()

    sql = f"INSERT INTO services (section, name, price, status) " \
          f"VALUES (%s, %s, %s, %s)"
    values = (service['section'], service['name'], service['price'], service['status'])
    mycursor.execute(sql, values)

    db.commit()

    print(mycursor.rowcount, "record inserted.")
    mycursor.close()
    db.close()


def get_all_services(filter: str):
    db = init_db()
    mycursor = db.cursor()

    if filter == 'all':
        sql = "SELECT * FROM services"
    else:
        sql = "SELECT * FROM services WHERE status = 'Available'"

    mycursor.execute(sql)

    services = mycursor.fetchall()
    result: list = []
    for service in services:
        _dict = {
            '_id': service[0],
            'section': service[1],
            'name': service[2],
            'price': service[3],
            'status': service[4]
        }
        result.append(_dict)
    mycursor.close()
    db.close()
    return result


def get_service_info(_id: str):
    db = init_db()
    mycursor = db.cursor()

    mycursor.execute(f"SELECT * FROM services WHERE _id = {_id}")

    service = mycursor.fetchall()[0]
    _dict = {
        '_id': service[0],
        'section': service[1],
        'name': service[2],
        'price': service[3],
        'status': service[4]
    }
    mycursor.close()
    db.close()
    return _dict


def update_service(_id: str, service: dict):
    old_service = get_service_info(_id)
    db = init_db()
    for key in service:
        if service[key] != old_service[key]:
            mycursor = db.cursor()

            sql = f"UPDATE services SET {key} = '{service[key]}' WHERE _id = {_id}"

            mycursor.execute(sql)

            db.commit()

            print(mycursor.rowcount, "record(s) affected")
            mycursor.close()

    db.close()


def delete_service(_id: str):
    db = init_db()
    mycursor = db.cursor()

    sql = f"DELETE FROM services WHERE _id = {_id}"

    mycursor.execute(sql)

    db.commit()

    print(mycursor.rowcount, "record(s) deleted")
    mycursor.close()
    db.close()




