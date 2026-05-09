#Login
#This py file will handle the login section
import sqlite3
import logging
from connection import session
#-------------------------------------------------------------------------
def start_login():
    session.set_user("kwstas",1)
    print("user and user_id are now set")

#-------------------------------------------------------------------------


    

