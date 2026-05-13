#Dashboard.py
#This py file will handle the dashboard section
#This is the entry point, all file paths will be guided from here
import sqlite3
import os
import logging #Logging will let us collect error logs from users
from login_system import login
from database import database
from login_system import auth

#-------------------------------------------------------------------------
#function to define basic logging for errors
def setup_logging():
    logging.basicConfig(
        filename=os.path.join("logs", "app.log"), #File name
        level=logging.ERROR, #Write only errors
        #See more at https://docs.python.org/3/library/logging.html
        format='%(asctime)s | %(levelname)s | %(message)s | %(module)s'
        )
    
#-------------------------------------------------------------------------
    
#main function of the program
def main():
    setup_logging() #start logging
    try:
        con = database.connect() #connect to database
        if con:
            loged_in = auth.check_login() #check if user is loged in
            if (loged_in):
                print("user is loged in!!") 
            else:
                print("redirecting to log in page")
                login.start_login()
                #get current user (it will be only id when we have data from db
                active_user = auth.get_user()
                if active_user:
                    print(f"Welcome {active_user.username} with id:{active_user.id}!!")
            
        else:
            print("There was a problem while creating the tables")
            
    #if program crashes for other reason write to logfile
    except Exception as e:
        logging.exception("Critical Error: The application crashed")
#-------------------------------------------------------------------------

#start main if we are only at dashboard (run this if the file was executed directly)
if __name__ == "__main__":
    main()
    


