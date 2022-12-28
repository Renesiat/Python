#!C:/Python311/python.exe

import os, base64
import mysql.connector
import db   # config for db connection
import dao  # User, UserDAO

# Authorization Server

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

# Перевіряємо схему авторизації - має бути Basic
if auth_header.startswith( 'Basic' ) :
    credentials = auth_header[6:]
else :
    send401( "Authorization scheme Basic required" )
    exit()

# credentials (параметр заголовку) - це Base64 кодований рядок "логін:пароль"
# у скрипті info підготуємо зразок для "admin:123"  --> YWRtaW46MTIz
# декодуємо credentials
try :
    data = base64.b64decode( credentials, validate=True ).decode( 'utf-8' )
except :
    send401( "Credentials invalid: Base64 string required" )
    exit()

# Перевіряємо формат (у data має бути :)
if not ':' in data :
    send401( "Credentials invalid: Login:Password format expected" )
    exit()

user_login, user_password = data.split( ':', maxsplit = 1 )

# підключаємось до БД
try :
    db = mysql.connector.connect( **db.conf )
except mysql.connector.Error as err :
    send401( err )
    exit()

# підключаємо userdao
user_dao = dao.UserDAO( db )

user = user_dao.read_auth( user_login, user_password )

if user is None :
    send401( "Credentials rejected" )
    exit()

# Auth: у разі успішної перевірки логіну та паролю
# перевірити чи є для цього користувача активний токен доступу -
# якщо є, то повернути його (не генерувати новий), інакше створити новий
# **якщо є токен, але його час валідності мешне за 10 хв, то можна перегенерувати
# SELECT * FROM access_tokens t 
# WHERE t.user_id = '..' AND t.expires > CURRENT_TIMESTAMP 
# ORDER BY t.expires DESC 
# LIMIT 1

# спочатку перевіряємо чи є активний токен для цього користувача

# генеруємо токен для даного користувача
access_token = dao.AccessTokenDAO( db ).create( user )
if not access_token :
    send401( "Token creation error" )
    exit()

# Успішне завершення
print( "Status: 200 OKey" )
print( "Content-Type: application/json; charset=UTF-8" )
print( "Cache-Control: no-store" )
print( "Pragma: no-cache" )
print()
print( f'''{{
  "access_token": "{access_token.token}",
  "token_type": "Bearer",
  "expires": "{access_token.expires}"
}} ''', end='' )


# An example of such a (https://datatracker.ietf.org/doc/html/rfc6750 page 9)
#    response is:

#      HTTP/1.1 200 OK
#      Content-Type: application/json;charset=UTF-8
#      Cache-Control: no-store
#      Pragma: no-cache
#      {
#        "access_token":"mF_9.B5f-4.1JqM",
#        "token_type":"Bearer",
#        "expires_in":3600,
#        "refresh_token":"tGzv3JOkF0XG5Qx2TlKWIA"
#      }