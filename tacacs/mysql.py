import pymysql

username = 'root'
passwd = 'root'
host = 'localhost'
database = 'tacacs'


def select(query):
    conn = pymysql.connect(user=username, passwd=passwd, host=host, database=database)
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    result = cursor.fetchall()
    conn.close()
    return result


def insert(query):
    conn = pymysql.connect(user=username, passwd=passwd, host=host, database=database)
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.commit()
    conn.close()


def delete(query):
    conn = pymysql.connect(user=username, passwd=passwd, host=host, database=database)
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.commit()
    conn.close()


def update(query):
    conn = pymysql.connect(user=username, passwd=passwd, host=host, database=database)
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.commit()
    conn.close()
