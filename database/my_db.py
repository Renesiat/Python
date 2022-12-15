import mysql.connector
connection_info={
    "host": "localhost",
    "port": 3306,
    "database": "py192",
    "user": "py192_user",
    "password": "pass_192"
}

def show_databases(connection):
    cursor = connection.cursor()
    sql="SHOW DATABASES"
    cursor.execute(sql)
    print("---------------------")
    print(cursor.description[0][0])
    for row in cursor:
        print(row)


def show_tables(connection):
    cursor = connection.cursor()
    sql= "SHOW TABLES "
    cursor.execute(sql)
    print("---------------------")
    print(cursor.description[0][0])
    for row in cursor:
        print(row)
          

def main():
    try :
        connection = mysql.connector.connect(**connection_info)
    except mysql.connector.Error as err:
        print(err, err)
    else:
        print("Connection OK")
        show_databases(connection)
        show_tables(connection)

if __name__ == "__main__":
    main()