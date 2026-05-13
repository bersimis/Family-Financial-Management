#Login.py
#This py file will handle the login section
import sqlite3
import logging
from login_system import auth
from database import database

input_user = "kwstas"
input_password = "123456"

#-------------------------------------------------------------------------
def start_login():
    #Here we will connect user by checking the right credentials
    con = database.connect() #First we will connect to database
    
    if con:
        #make the cursor
        cur = con.cursor()

        try:
            #execute the querie
            cur.execute("""
            SELECT id,username,role_id
                FROM users
                WHERE username=? AND password=?
            """, (input_user,input_password)) 
            #take result from querie
            result = cur.fetchone()
            
            if result: #if result is not None
                #get result (its a list)
                correct_user_id = result[0]
                correct_username = result[1]
                correct_role_id = result[2]
                #send correct credentials to auth
                auth.set_user(correct_user_id,correct_username,correct_role_id)
            else:
                print("Wrong credentials")
        except Exception as e:
            logging.exception("An error occurred during login.")

        finally:
            #close the connection
            con.close()
        
    
#-------------------------------------------------------------------------


    

