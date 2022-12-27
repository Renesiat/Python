
import os

envs = "<ul>" + ''.join( f"<li>{k} = {v}</li>" for k,v in os.environ.items() ) + "</ul>"


html = f"""<!doctype html />
<html>
<head>
</head>
<body>
    <h1>Hello CGI World</h1>
    
</body>
</html>"""


                                      
print( "Content-Type: text/html; charset=utf-8" )    
print( f"Content-Length: {len(html)}" )
print( "" )                          
print( html )                         
                                     
                                     
