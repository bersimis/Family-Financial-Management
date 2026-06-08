#database.py
#This py file will handle the connection that is needed in order
#to connect to database
import sqlite3
import os
import logging


#-------------------------------------------------------------------------

#first we will connect to DB
def connect():
    db_dir = "database"
    db_filepath = os.path.join(db_dir, "financial_management.db")
    
    #Create database directory if it does not exist
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    #First time that will run it will create the db if not exist and tables
    #We will use the variable below to store the filepath before the filepath
    #Is created to know if to run create_db(con) or not.
    db_exists = os.path.exists(db_filepath)    
    #Connect to db
    try:
        con = sqlite3.connect(db_filepath) #It will create the db file if not exist
        cur = con.cursor()
        #Activate Foreign Keys
        cur.execute("PRAGMA foreign_keys = ON;")
        
        if not db_exists:
            create_db(con) #Create tables
            
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

            
        /*Insert the rolles in the table rolles */
         INSERT OR IGNORE INTO roles (name) VALUES 
            ('admin'), 
            ('editor'), 
            ('viewer');
            
        /* Insert Power user named admin with password 'admin' (hashed) on first program run */
        INSERT OR IGNORE INTO users (username, password, role_id, birth_year, age) 
        VALUES (
            'admin', 
            '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', /* This is hashed */
            (SELECT id FROM roles WHERE name = 'admin'), 
            1900, 
            2026-1900 
        );
    """)
    con.commit()  # save changes
