import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class MainHandler( BaseHTTPRequestHandler ) :
    def do_GET( self ) -> None :
        print( self.path )    # вивід у консоль
        path_parts = self.path.split( '/' )  # розділення запиту по /
        # оскільки всі запити починаються з /, path_parts[0] - завжди порожній
        if path_parts[1] == "" :
            path_parts[1] = "index.html"
        # перевіряємо чи path_parts[1] відповідає за існуючий файл
        fname = ( './http/' +     # './http/' - папка з файлом серверу
                path_parts[1] )          
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

        self.send_200( user_login + user_password )
        return 
    # Д.З. Забезпечити "глибокий" пошук файлів (у інших папках): для цього
    #  - створити папки css та js
    #  - створити у них по файлу (style.css, script.js)
    #  - у index.html підключити ці файли, пересвідчитись у їх роботі
    # (у стилі - достатньо мінімальних стилів, у script.js перенести з index.html)

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
    http_server = HTTPServer( 
        ( '127.0.0.1', 88 ),     # host + port = endpoint
        MainHandler )
    try :
        print( "Server started" )
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
'''