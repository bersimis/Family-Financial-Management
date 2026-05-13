#Register.py
#This will handle the registretion of a user
import sqlite3
import logging
import string # for the use of pool logic
import datetime # we need to find (thisYear) for age logic
from database import database
from login_system import auth

user_input = "Name"
password_input = "123456789"
birth_year_input = 1994

#-------------------------------------------------------------------------
def register():
    #here we will write the code to register user after button click
    con = database.connect() #connect to database
    
    #check if username and password have correct data so we can
    #run the query
    correct_username = check_username(user_input)
    correct_password = check_password(password_input)
    correct_birth_year = check_birthyear(birth_year_input)
    role_id = 3 # All new users will log in as viewers id=3 until admin changes their access
    if correct_birth_year:
        #calculate users age
        user_age = datetime.datetime.now().year - birth_year_input
        
    if (correct_username and correct_password and correct_birth_year):
        
        if con:
            #make the cursor
            cur=con.cursor()
            try:
                cur.execute("""
                    INSERT INTO users (username,password,birth_year,age,role_id)
                    VALUES (?,?,?,?,?)
                """,(user_input,password_input,birth_year_input,user_age,role_id))
                con.commit()
            except Exception as e:
                logging.exception("An error occured during register.")
            finally:
                #close the connection
                con.close()
           
            
#-------------------------------------------------------------------------
            
def check_username(user_input):
    #create a pool to check data from user to validate the input
    valid_username = string.ascii_letters + string.digits
    #run loop to check it
    for char in user_input:
        #if characher is not inside the pool (valid char) then return false
        if char not in valid_username:
            print("You must put letters and numbers only")
            return False
    #After the loop if nothing is False return True   
    return True
#-------------------------------------------------------------------------

def check_password(password_input):
    #here we will check if password meets security requirements
    
    #check the length of string has to be >=8
    if len(password_input)<8:
        print("Password must be at least 8 characters long")
        return False
    
    #create a pool to check data from user to validate the password
    #We dont want sertain special chars becose we want to protect from
    #SQL injection
    valid_password = string.ascii_letters + string.digits + "!@#$%"
    
    for char in password_input:
        if char not in valid_password:
            print("Correct characters are a-z,A-Z,1-9,!@#$%")
            return False
                 
    #After the loop if nothing is False return True
    return True
#-------------------------------------------------------------------------

def check_birthyear(birth_year_input):
    #here we will check if birthyear is from 1900 to (thisYear -1)
    #we just need valid input its not our job to tell a baby if it wants
    #to track family finances
    this_year = datetime.datetime.now().year
    if birth_year_input >= 1900 and birth_year_input<=this_year-1:
        return True
    else:
        return False 
        
