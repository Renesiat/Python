# Робота з БД: таблиця Users
import datetime
import hashlib    # засоби гешування
import mysql.connector
import random
import time 
import uuid

class User :
    def __init__( self, row = None ) -> None :
        if row == None :
            self.id         = None
            self.login      = None
            self.passw      = None
            self.name       = None
            self.salt       = None
            self.avatar     = None
            self.email      = None
            self.email_code = None
            self.del_dt     = None
        elif isinstance( row, dict ) :
            self.id         = row["id"]
            self.login      = row["login"]
            self.passw      = row["pass"]
            self.name       = row["name"]
            self.salt       = row["salt"]
            self.avatar     = row["avatar"]
            self.email      = row["email"]
            self.email_code = row["email_code"]
            self.del_dt     = row["del_dt"]
        else :
            raise ValueError( "row type unsuppotred" )

    def __str__( self ) -> str :
        return str( self.__dict__ )

    __repr__ = __str__


class UserDAO :
    def __init__( self, db: mysql.connector.MySQLConnection ) -> None :
        self.db = db

    def make_salt( self, len: int = 20 ) -> str :
        ''' Generates crypto-salt with 'len' bytes entropy'''
        return random.randbytes( len ).hex()

    def hash_passw( self, passw: str, salt: str ) -> str :
        return hashlib.sha1( (passw + salt).encode() ).hexdigest()

    def make_email_code( self ) -> str :
        return self.make_salt(3)  # 3 bytes == 6 hex-symbols

    def create( self, user: User ) -> None :
        ''' Inserts 'user' into DB table. 
            user.passw - plain password, 
            salt and hash will be generated,
            email_code will be generated too'''
        cursor = self.db.cursor()
        user.id = str( uuid.uuid4() )
        user.salt = self.make_salt()
        user.passw = self.hash_passw( user.passw, user.salt )
        user.email_code = self.make_email_code()
        ks = user.__dict__.keys()
        sel  = ','.join( f"`{x}`" for x in ks ).replace( 'passw', 'pass')
        vals = ','.join( f"%({x})s" for x in ks )
        sql = f"INSERT INTO Users({sel}) VALUES({vals})"
        try :
            cursor.execute( sql, user.__dict__ )
            self.db.commit()
        except mysql.connector.Error as err :
            print( err )
        else :
            print( "Create OK" )
        finally :
            cursor.close()
        return

    def read( self, id = None, login = None, ignore_deleted = True ) -> tuple | None :
        sql = "SELECT u.* FROM `users` u "
        par = []
        if id :
            sql += "WHERE u.`id` = %s "
            par.append( id )
        if login :
            sql += ( "AND" if id else "WHERE" ) + " u.`login` = %s "
            par.append( login )
        if ignore_deleted :
            sql += ( "AND" if id or login else "WHERE" ) + " u.`del_dt` IS NULL "

        try :
            cursor = self.db.cursor( dictionary = True )
            cursor.execute( sql, par )
        except mysql.connector.Error as err :
            print( 'read:', err )
        else :
            return tuple( User(row)  for row in cursor )
        finally :
            cursor.close()
        return None

    def read_auth( self, login, password ) -> User | None :
        user = ( self.read( login = login ) + (None,) )[0]   # None - for empty list OR user
        # оскільки видалення - це мітка часу, враховуємо це при авторизації
        if user \
            and user.del_dt == None \
            and self.hash_passw( password, user.salt ) == user.passw :
                return user
        return None
    
    def update( self, user: User ) -> bool :
        # з user беремо id, інші поля оновлюються
        # "UPDATE `users` u SET u.`login`= %(login)s, u.`name` = %(name)s   WHERE u.`id` = %(id)s "
        fields = user.__dict__.keys()
        sql = "UPDATE `users` u SET " + \
            ','.join( f"u.`{field.replace('passw', 'pass')}` = %({field})s"  for field in fields if field != 'id' ) + \
            " WHERE u.`id` = %(id)s "
        # print( sql )
        try :
            cursor = self.db.cursor()
            cursor.execute( sql, user.__dict__ )
            self.db.commit()
        except mysql.connector.Error as err :
            print( 'update', err )
        else :
            return True
        finally :
            cursor.close()
        return False

    def delete( self, user: User ) -> bool :
        # через наявність реляцій у БД видаляти інформаційні одиниці ДУЖЕ не бажано
        # одна з найпростіших реалізацій видалення - створення додаткового поля
        # 'del_dt' з міткою часу моменту видалення. Складніше - ведення окремої таблиці видалень
        try :
            cursor = self.db.cursor()
            user.del_dt = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime() )
            cursor.execute( "UPDATE users u SET u.del_dt = %s WHERE u.id = %s", (user.del_dt, user.id,) )
            self.db.commit()            
        except mysql.connector.Error as err :
            print( 'delete', err )
        else :
            return True
        finally :
            try : cursor.close()
            except : pass
        return False

# Д.З. скласти методи UserDAO:
#  restore(user) - відновлення користувача (з видалених)
#  is_login_free( login: str ) - який проводить пошук як серед активних, так і серед
#   видалених користувачів (можна на базі read)
# переконатись у встановленні Apache - веб-сервера


def main( db_conf ) -> None :
    try :
        db = mysql.connector.connect( **db_conf )
    except mysql.connector.Error as err :
        print( err.errno, err )
        return

    print( "Connection OK" )
    # user = User()
    # user.login = "guest"
    # user.email = "guest@ukr.net"
    # user.name  = "Guest Walker"
    # user.passw = "123"
    # user.login = "user"
    # user.email = "user@ukr.net"
    # user.name  = "Experienced User"
    # user.passw = "123"
    userDao = UserDAO( db )
    # userDao.create( user )
    # print( userDao.read() )
    #(user,) = userDao.read( id = 'd8df8963-0c16-4c9a-a85e-b6c35dfaa48a' ) + (None,) ; print( user )    
    #(user,) = userDao.read( id = '!d8df8963-0c16-4c9a-a85e-b6c35dfaa48a' ) + (None,) ; print( user )    
    #(user,) = userDao.read( login = 'user' ) + (None,) ; print( user )    
    #(user,) = userDao.read( login = '!user' ) + (None,) ; print( user )    
    # print( (userDao.read( login = 'user' ) + (None,))[0] )

    # print( userDao.read_auth( 'admin', '123' ) )
    # print( userDao.read_auth( 'admin', '1234' ) )
    # print( userDao.read_auth( 'odmin', '1234' ) )
    # ( user ) = userDao.read_auth( 'user', '123' )
    ( user ) = userDao.read_auth( 'guest', '123' )
    # user.email = "user@meta.ua"
    # userDao.update( user )
    # userDao.delete( user )
    print( user )
    return


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

# Організувати збереження конфігураційних даних (про підключення до БД)
# у окремому файлі. Підключати файл у робочій програмі

'''
Скопіюємо таблицю (декларацію) з попереднього проєкту (Java)
show create table users;
CREATE TABLE `users` (
  `id`     char(36)     NOT NULL DEFAULT uuid() COMMENT 'UUID',
  `login`  varchar(64)  NOT NULL,
  `pass`   char(40)     NOT NULL COMMENT 'SHA-160 hash',
  `name`   varchar(128) NOT NULL,
  `salt`   char(40)     DEFAULT NULL,
  `avatar` varchar(64)  DEFAULT NULL COMMENT 'Avatar filename',
  `email`  varchar(64)  DEFAULT NULL COMMENT 'User E-mail',
  `email_code` char(6)  DEFAULT NULL COMMENT 'E-mail confirmation code',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

ALTER TABLE users ADD COLUMN del_dt DATETIME DEFAULT NULL ;

ORM : відображення даних на об'єкти  -  cтворення класів, структура
яких відповідає структурі таблиць

'''