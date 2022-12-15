import mysql.connector
import config_json

def main( db_conf ) -> None :
    try :
        connection = mysql.connector.connect( **db_conf )
    except mysql.connector.Error as err :
        print( err.errno, err )
    else :
        print( "Connection OK" )
    return


if __name__ == "__main__" :
    
    main(  config_json.from_json() )