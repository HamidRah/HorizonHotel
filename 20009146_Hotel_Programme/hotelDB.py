# Hamidur Rahman: 20009146
import os
from dotenv import load_dotenv       
import mysql.connector
from mysql.connector import errorcode

load_dotenv()                       

# pull credentials from the environment
hostname = os.getenv("DB_HOST", "127.0.0.1")    
username = os.getenv("DB_USER", "root")
passwd   = os.getenv("DB_PASSWORD")              
db       = os.getenv("DB_NAME", "horizonhotel")

def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              database=db)  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)                        
    else:  #will execute if there is no exception raised in try block
        return conn   
                
