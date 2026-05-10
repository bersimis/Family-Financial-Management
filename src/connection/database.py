#Connection
#This py file will handle the connection that is needed in order
#to connect to database
import sqlite3
import os
import logging


#-------------------------------------------------------------------------

#first we will connect to DB -> session/financial_management.py
def connect():
    db_filepath = os.path.join("connection", "financial_management.db")
    
    #first time that will run it will create the db if not exist and tables
    #we will use the variable below to store the filepath before the filepath
    #is created to know if to run create_db(con) or not.
    db_exists = os.path.exists(db_filepath)    
    #Connect to db
    try:
        con = sqlite3.connect(db_filepath) # it will create the db file if not exist
        cur = con.cursor()
        #Activate Foreign Keys
        cur.execute("PRAGMA foreign_keys = ON;")
        print("Database connection success")
        
        if not db_exists:
            create_db(con) # create tables
            
        return con
    except Exception:
        logging.exception("Couldnt connect to database")
        return None
    
#-------------------------------------------------------------------------

def create_db(con):
    #Create the database structure
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role_id INTEGER NOT NULL,               
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            birth_year INTEGER NOT NULL,
            age INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles (id) 
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense'))  /*We will check that only values income or expence will be inserted into the Db*/
                                                                     /*this ensures proper and acurate dada*/
        );

        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL CHECK (amount>=0),   /*We will check if the user puts negative values we will only need >=0*/
            date TEXT NOT NULL,
            is_monthly INTEGER DEFAULT 0 CHECK (is_monthly IN (0,1)), /*We will use is_montly 0 and 1 as flag for proper data handling regarding repetitive expences or incomes*/
            created_by INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id), /* FK of categories*/
            FOREIGN KEY (created_by) REFERENCES users (id)        /* FK of users */
        );
    """)
    con.commit() #save changes
    
#-----------------------------------------------------------------------
    
    
