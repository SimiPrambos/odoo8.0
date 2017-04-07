import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "popo",
                           db = "flaskapp")
    c = conn.cursor()

    return c, conn