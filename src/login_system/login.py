#Login.py
#This py file will handle the login section
import sqlite3
import logging
import hashlib # Added for password hashing verification
from login_system import auth
from database import database

input_user = "admin1"
input_password = "admin"

#-------------------------------------------------------------------------
def start_login():
    #Here we will connect user by checking the right credentials after button click
    con = database.connect() #First we will connect to database
    
    if con:
        #make the cursor
        cur = con.cursor()
        
        try:
            # Hash the input password to compare it with the stored hash in the DB
            hashed_input = hashlib.sha256(input_password.encode()).hexdigest()

            #execute the query
            #We now compare the hashed_input with the hashed password in the database
            cur.execute("""
            SELECT id,username,role_id
                FROM users
                WHERE username=? AND password=?
            """, (input_user, hashed_input)) 

            #take result from query
            result = cur.fetchone()
            
            if result: #if result is not None
                #get result (its a tuple)
                correct_user_id = result[0]
                correct_username = result[1]
                correct_role_id = result[2]
                
                #send correct credentials to auth
                auth.set_user(correct_user_id, correct_username, correct_role_id)
                print(f"Login successful! Welcome {correct_username}")
            else:
                print("Wrong credentials")

        except Exception as e:
            logging.exception("An error occurred during login.")

        finally:
            #close the connection
            con.close()
#-------------------------------------------------------------------------
