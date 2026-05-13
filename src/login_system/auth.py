#auth.py
#This py file will handle the session of current_user
import sqlite3
import os
import logging
#-------------------------------------------------------------------------

#Create the classfor user
class User:
    #create the method
    def __init__(self,id,username,role_id):
        self.id = id
        self.username = username
        self.role_id = role_id
#-------------------------------------------------------------------------

#First time program runs user is None
current_user = None
def check_login():
    #if user is None then return false and redirect user to login page
    if current_user is not None: 
        return True
    else:
        #the user is loged in (let user visit dashboard)
        return False
#-------------------------------------------------------------------------
    
#We will create and set the User object passed by login.py
def set_user(user_id, username, role_id):
    global current_user
    #create the object of user
    current_user = User(user_id, username, role_id)
#-------------------------------------------------------------------------    

#we will return user id to dashboard (this will get as all data
#from current user after we connect it to database for now
#it will only pass static id and name for testing
def get_user():
    return current_user

#-------------------------------------------------------------------------

