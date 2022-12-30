#!C:/Users/Lin/AppData/Local/Programs/Python/Python311/python.exe


import os
import cgi, cgitb

import json
# Задание: реализовать работу кнопки "Контент" (запрос на /items):

# - если нет токена в заголовках, то ответ 401

# - формат заголовка:  Bearer e5d7494f8ec94d3dccdc9a19e014b0f39d9d4f2a

#     обеспечить проверку формата

# - проверить токен на валидность, в случае успеха выдать контент - перечень

#     пользователей и их эл. почты,

#     иначе - 401
    
envs = "<ul>" + ''.join( f"<li>{k} = {v}</li>" for k,v in os.environ.items() ) + "</ul>"

json_object = json.dumps(envs)

with open("environ_items.json", "w") as outfile:
        outfile.write(json_object)
        
html = f"""<!doctype html />
<html>
<head>
</head>
<body>
    <h1>Hello </h1>
    {envs}
   
 <form action = "x=10&y=20" method = "get">
    GET METHODS <input type = "submit" value = "Submit" />
</form>
</form>
</body>
</html>"""


                                 
print( "Content-Type: text/html; charset=utf-8" )    # далі ідуть заголовки
print( f"Content-Length: {len(html)}" )
print( "" )                           # тіло відокремлюється порожнім рядком
print( html )                         # далі іде тіло. За наявності тіла вимагається наявність
                                      # заголовків Content-Type: та Content-Length:

                                  # Через потребу Content-Length тіло формують окремо


# Налагодження:
#  1. Створюємо локальний хост (сайт) із зазначенням CGI режиму
#     - створюємо папку для сайта (C:\Users\_dns_\source\repos\Py192\cgi), 
#         створюємо у ній файл index.py 
#         у ньому: зазначаємо шлях до інтерпретатора
#         та команду виведення коду HTML
#     - знаходимо файли конфігурації Apache (httpd-vhosts.conf або httpd.conf)
#     - додаємо відомості про новий хост (як правило, є зразок)
#         <VirtualHost *:80>
#             ServerAdmin webmaster@localhost
#             DocumentRoot "C:/Users/_dns_/source/repos/Py192/cgi"
#             ServerName py192.loc
#             ErrorLog "C:/Users/_dns_/source/repos/Py192/cgi/error.log"
#             CustomLog "C:/Users/_dns_/source/repos/Py192/cgi/access.log" common
#             <Directory "C:/Users/_dns_/source/repos/Py192/cgi">
#                 AllowOverride All
#                 Options -Indexes +ExecCGI
#                 AddHandler cgi-script .py
#                 Require all granted
#             </Directory>
#         </VirtualHost>
#     - знаходимо файл конфігурації httpd.conf, знаходимо рядок (~286) з 
#         DirectoryIndex  index.php index.pl ... (додаємо) index.py
#       зберігаємо конфігурації і обов'язково перезапускаємо Apache  
#         ознакою успішного створення локального хосту є поява файлів error.log, access.log
#         у заявленій папці. Можна додати ці файли до .gitignore

#  2. Реєструємо адресу нового сайту у локальній DNS: відкриваємо файл 
#        C:\Windows\System32\drivers\etc\hosts  (у режимі адміністратора)
#        /etc/hosts
#        додаємо рядки з іменем хоста (ServerName)
#        	127.0.0.1       py192.loc
# 	    ::1             py192.loc

#  3. Запускаємо браузер та вводимо повністю http://py192.loc

# '''