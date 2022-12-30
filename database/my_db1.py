# Робота з БД. Продовження
import mysql.connector
import random

def select_dicts( db : mysql.connector.MySQLConnection, order='U' ) -> tuple :
    sql = "SELECT * FROM test t ORDER BY " + ( 't.str' if order == 'G' else 't.ukr' )
    try :
        cursor = db.cursor()    
        cursor.execute( sql )  
    except mysql.connector.Error as err :
        print( 'select_dicts:', err )
    else :
        # names = cursor.column_names   # zip - (zipper "застібка-блискавка") - поєднує 
        # row = cursor.fetchone()       # елементи першої множини з елементами другої: 1й-з 1м, 2й-з 2м,...
        # print( dict( (k,v) for k,v in zip( names, row ) ) )
        return ( dict( (k,v) for k,v in zip( cursor.column_names, row ) ) 
                 for row in cursor )
    finally :
        try: 
            db.commit()  
            cursor.close()
        except: pass
    return

def select_test( db : mysql.connector.MySQLConnection, order='U' ) -> None :
    ''' Prints table 'test' data depending on 'order' parameter: 'U'(default)-Unicode, 'G'-General '''
    sql = "SELECT * FROM test t ORDER BY " + ( 't.str' if order == 'G' else 't.ukr' )
    try :
        cursor = db.cursor()    
        cursor.execute( sql )  
    except mysql.connector.Error as err :
        print( 'SELECT:', err )
    else :
        # while True :
        #     row = cursor.fetchone()   # передача даних від БД іде по одному рядку
        #     if not row : break        # ознакою кінця даних є None y row
        #     print(row)
        print( cursor.column_names )
        for row in cursor :    # можна ітерувати сам cursor - це повністю аналогічно    
            print( row )       # попередньому циклу
    finally :
        try: 
            db.commit()     # InternalError("Unread result found") - якщо не всі дані "забрано"
            cursor.close()
        except: pass
    return


def rand_str() -> str :
    alf = "АБВГҐДЕЄЖЗИІЇКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    return ''.join( random.choice(alf) for i in range( random.choice([3,4,5]) ) )


def insert_test( db : mysql.connector.MySQLConnection ) -> None :
    ''' Inserts random values into 'test' table '''
    sql = "INSERT INTO test( num, str, ukr ) VALUES ( %s, %s, %s )"
    str = rand_str()
    num = random.randint(1, 20)
    try :
        cursor = db.cursor()                     # відкриття курсора - створює транзакцію
        cursor.execute( sql, (num, str, str) )   # виконання команди - планується
    except mysql.connector.Error as err :
        print( 'INSERT:', err )
    else :
        print( 'INSERT: OK' )
    finally :
        db.commit()
        cursor.close()                           # закриття курсора без коміту транзакції - відміняє її
    return     
   

def create_table( db : mysql.connector.MySQLConnection ) -> None :
    ''' Creates table 'test' in DB '''
    sql = '''
    CREATE TABLE `users` (
        `id` char(36) NOT NULL DEFAULT uuid() COMMENT 'UUID',
        `login` varchar(64) NOT NULL,
        `pass` char(40) NOT NULL COMMENT 'SHA-160 hash',
        `name` varchar(128) NOT NULL,
        `salt` char(40) DEFAULT NULL,
        `avatar` varchar(64) DEFAULT NULL COMMENT 'Avatar filename',
        `email` varchar(64) DEFAULT NULL COMMENT 'User E-mail',
        `email_code` char(6) DEFAULT NULL COMMENT 'E-mail confirmation code',
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
'''
    try :
        cursor = db.cursor()
        cursor.execute( sql )
    except mysql.connector.Error as err :
        print( 'CREATE:', err )
    else :
        print( 'CREATE: OK' )
    finally :
        cursor.close()
    return 
    print()


def main( db_conf ) -> None :
    try :
        connection = mysql.connector.connect( **db_conf )
    except mysql.connector.Error as err :
        print( err.errno, err )
    else :
        print( "Connection OK" )
        create_table( connection )
        insert_test( connection )
        select_test( connection )
        print( select_dicts( connection ) )
        for d in select_dicts( connection ) :
            print( d["num"], d["str"] )
    return
    print("created")


if __name__ == "__main__" :
    db_conf = {
        "host":     "localhost",
        "port":     3306,
        "database": "py192",
        "user":     "py192_user",
        "password": "pass_192",

        "use_unicode": True,
        "charset":     "utf8mb4",
        "collation":   "utf8mb4_general_ci"
    }
    main( db_conf )