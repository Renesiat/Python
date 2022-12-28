#!C:/Python311/python.exe

import os
# API demo - доступ до ресурсу обмеженого доступу (Resource Server)

def send401( message:str = None ) -> None :
    print( "Status: 401 Unauthorized" )
    if message : print( 'Content-Type: text/plain" ')
    print()
    if message : print( message )
    return
    
    
# дістаємо заголовок Authorization
if 'HTTP_AUTHORIZATION' in os.environ.keys() :
    auth_header = os.environ['HTTP_AUTHORIZATION']
else :
    # відправляємо 401
    send401()
    exit()

if auth_header.startswith( 'Bearer' ) :
    token = auth_header[7:]
else :
    send401( "Authorization scheme Bearer required" )
    exit()

# Перевіряємо токен
import mysql.connector
import db
import dao
# підключаємось до БД
try :
    db = mysql.connector.connect( **db.conf )
except mysql.connector.Error as err :
    send401( err )
    exit()

# підключаємо userdao
user_dao = dao.UserDAO( db )

user = user_dao.read( token ) 
if not user :
    send401( "Token rejected" )
    exit()

# Успішне завершення
print( "Status: 200 OK" )
print( "Content-Type: application/json; charset=UTF-8" )
print()
print( f'"{token}"' )



# '''
# Схеми авторизації.
# https://datatracker.ietf.org/doc/html/rfc6750

# Запит на обмежений ресурс --> Перевірка авторизації
# якщо "+", то видаємо ресурс, інакше відповідь з кодом 401

# Перевірка авторизації: аналіз заголовку Authorization
# та відповідної схеми автентифікації
#  - Basic - безпосередня передача логіну та паролю (кодованих у Base64)
#  - Bearer - за допомогою спеціальних токенів

# Токен отримується від серверу авторизації /auth
#
# Робота з токенами: ведеться жунал видачі токенів
# CREATE TABLE access_tokens( 
#   token CHAR(40) PRIMARY KEY,
#   expires DATETIME NOT NULL,
#   user_id CHAR(36) NOT NULL,
#   FOREIGN KEY (user_id) REFERENCES users(id)
# ) ENGINE=InnoDB, DEFAULT CHARSET=UTF8
#
#
#
# '''