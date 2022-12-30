import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import mysql.connector
import sys
sys.path.append( './cgi/api/' )
import db
import dao

# Задание: реализовать работу кнопки "Контент" (запрос на /items):

# - если нет токена в заголовках, то ответ 401

# - формат заголовка:  Bearer e5d7494f8ec94d3dccdc9a19e014b0f39d9d4f2a

#     обеспечить проверку формата

# - проверить токен на валидность, в случае успеха выдать контент - перечень

#     пользователей и их эл. почты,

#     иначе - 401

class DbService :
    __connection:mysql.connector.MySQLConnection = None

    def get_connection( self ) -> mysql.connector.MySQLConnection :
        if DbService.__connection is None or not DbService.__connection.is_connected() :
            try :
                DbService.__connection = mysql.connector.connect( **db.conf )
            except mysql.connector.Error as err :
                print( err )
                DbService.__connection = None
        return DbService.__connection


class DaoService :

    def __init__( self, db_service ) -> None:
        self.__db_service: DbService = db_service
        self.__user_dao: dao.UserDAO = None                  
        self.__access_token_dao: dao.AccessTokenDAO = None   
        return

    def get_user_dao( self ) -> dao.UserDAO :
        if self.__user_dao is None :
            self.__user_dao = dao.UserDAO( self.__db_service.get_connection() )
        return self.__user_dao

    def get_access_token_dao( self ) -> dao.AccessTokenDAO :
        if self.__access_token_dao is None :
            self.__access_token_dao = dao.AccessTokenDAO( self.__db_service.get_connection() )
        return self.__access_token_dao



dao_service: DaoService = None

class MainHandler( BaseHTTPRequestHandler ) :
    def __init__( self, request, client_address, server ) -> None:
        super().__init__(request, client_address, server)   # RequestScoped - створюється при кожному запиті
        # print( 'init', self.command )    # self.command - метод запиту (GET, POST, ...)
    
    def do_GET( self ) -> None :
        print( self.path )
        path_parts = self.path.split( '/' )  

        if self.path == '/' :
            self.path = '/index.html'

        fname = ( './http' +     
                self.path )            
        if os.path.isfile( fname ) :
            self.flush_file( fname )
            return
        # Routing - розподіл роботи за запитами
        if path_parts[1] == "auth" :
            self.auth()
        else :
            self.send_response( 200 )
            self.send_header( "Content-Type", "text/html" )
            self.end_headers()
            self.wfile.write( "<h1>404</h1>".encode() )
            # self.flush_file( "./http/index.html" )
        return

    def auth( self ) -> None :
        # дістаємо заголовок Authorization
        auth_header = self.headers.get( "Authorization" )
        if auth_header is None :
            self.send_401( "Authorization header required" )
            return
        # Перевіряємо схему авторизації - має бути Basic
        if auth_header.startswith( 'Basic ' ) :
            credentials = auth_header[6:]
        else :
            self.send_401( "Authorization scheme Basic required" )
            return
        # декодуємо credentials
        try :
            data = base64.b64decode( credentials, validate=True ).decode( 'utf-8' )
        except :
            self.send_401( "Credentials invalid: Base64 string required" )
            return
        # Перевіряємо формат (у data має бути :)
        if not ':' in data :
            self.send_401( "Credentials invalid: Login:Password format expected" )
            return
        # Розділяємо логін та пароль за ":"
        user_login, user_password = data.split( ':', maxsplit = 1 )
        #self.send_200(user_login +'-'+ user_password)
        #return
        # підключаємо userdao
        user_dao = dao_service.get_user_dao()
        user = user_dao.read_auth( user_login, user_password )
        if user is None :
            self.send_401( "Credentials rejected" )
            return
# Д.З. Реалізувати генерацію токену за авторизованим користувачем
        self.send_200( user.id )
        return 
    def items( self ) -> None:   
        try:
        # дістаємо заголовок Authorization
            auth_header = self.headers.get( "Authorization" )

            if auth_header is None :
                self.send_401( "Authorization header required" )
                return

        # Перевіряємо схему авторизації
            if not auth_header.startswith( 'Bearer' ) :
                self.send_401( "Bearer authorization header required" )
                return

        # Берем токен
            data = auth_header[7:]
        
            access_dao = dao_service.get_access_token_dao()
            access_token = access_dao.get(data)
        
        #Перевіряємо валідацію
            if access_token is None:
                self.send_401( "Access token not validity" )
                return
        
            user_dao = dao_service.get_user_dao()
            users = user_dao.get_users()
        
            list = json.dumps(users)
        

            self.send_200(json.dumps(list))
        except Exception as error:
            print(error)
        finally:
            exit()


    def send_401( self, message:str = None ) -> None :
        self.send_response( 401, "Unauthorized"  )
        if message : self.send_header( "Content-Type", "text/plain" )
        self.end_headers()
        if message : self.wfile.write( message.encode() )
        return

    def send_200( self, message:str = None, type:str = "text" ) -> None :
        self.send_response( 200 )
        if type == 'json' :
            content_type = 'application/json; charset=UTF-8'
        else :
            content_type = 'text/plain; charset=UTF-8'
        self.send_header( "Content-Type", content_type )
        self.end_headers()
        if message:
            self.wfile.write( message.encode() )
        return

    def flush_file( self, filename ) -> None :
        # Визначаємо розширення файлу
        extension = filename[ filename.rindex(".") + 1 : ]
        # print( extension )
        # Встановлюємо тип (Content-Type)
        if extension == 'ico' :
            content_type = 'image/x-icon'
        elif extension in ( 'html', 'htm' ) :
            content_type = 'text/html'
        elif extension == 'css' :
            content_type = "text/css"
        elif extension == 'js' :
            content_type = "application/javascript"
        else :
            content_type = 'application/octet-stream'

        self.send_response( 200 )
        self.send_header( "Content-Type", content_type )
        self.end_headers()
        # Копіюємо вміст файлу у тіло відповіді
        with open( filename, "rb" ) as f :
            self.wfile.write( f.read() )
        return

    # Override
    def log_request(self, code: int | str = ..., size: int | str = ...) -> None:
        # логування запиту у консоль
        # return super().log_request(code, size)
        return


def main() -> None :
    global dao_service
    http_server = HTTPServer( 
        ( '127.0.0.1', 88 ),     # host + port = endpoint
        MainHandler )
    try :
        print( "Server started" )
        dao_service = DaoService( DbService() )   # ~ Inject
        http_server.serve_forever()       
    except :
        print( "Server stopped" )


if __name__ == "__main__" :
    main()

'''
Інший спосіб створення серверних додатків (поруч з CGI) - утворення
"власного" сервера, який прослуховує порт та запускає оброблення запитів.

Засоби:
 http.server - модуль
 HTTPServer - клас для старту сервера
 BaseHTTPRequestHandler - базовий клас для обробників запитів (~ Servlet)

Особливості (у порівнянні з CGI)
- сервер запускається засобами Python з консолі, відповідно print діє 
    як у скриптах - виводить у консоль (не у відповідь сервера)
- обробник запитів (Handler) - це клас нащадок BaseHTTPRequestHandler,
    його методи відповідають формі do_GET, do_POST, ... ,
    методи не приймають параметрів, усі дані про request|response
    проходять як поля/методи self.(send_response, send_header)
- формування тіла здійснюється за файловим протоколом через запис
    у self.wfile Особливість - він пише не рядки, а бінарні дані
- успішні запити логуються у консоль (127.0.0.1 - - [27/Dec/2022 12:45:15] "GET / HTTP/1.1" 200 - )
    за це відповідає метод log_request, який можна переозначити
- запити не маршрутизуються (всі потрапляють у do_GET), наявність 
    файлів не перевіряється (запити на файли також потрапляють у do_GET)
    Необхідно самостійно опрацьовувати запити на файли

    insert into users values( '9048dcfa-7b84-11ed-8d7a-14857fd97497','admin','cafcb5d4f280493e9b6a211320104ea58420d223','Root Administrator',
    '69c555d0a00f00815bdc0a88e7f6085a669e07db',NULL,'admin@gmail.com','c16ae2',0, NULL)
'''