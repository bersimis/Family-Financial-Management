#database.py
#This py file will handle the connection that is needed in order
#to connect to database
import sqlite3
import os
import logging


#-------------------------------------------------------------------------

#first we will connect to DB
def connect():
    # Path updated to look inside the database folder relative to src
    db_filepath = os.path.join("database", "financial_management.db")
    
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
    con.commit() #save changes
    
#-----------------------------------------------------------------------
    
# ---------------------------------------------------------------------
# GET CATEGORIES
# ---------------------------------------------------------------------
def get_categories(user_id, category_type):
    con = connect()

    if con is None:
        return []

    try:
        cur = con.cursor()

        cur.execute("""
            SELECT id, name, type
            FROM categories
            WHERE type = ?
            ORDER BY name
        """, (category_type.lower(),))

        return cur.fetchall()

    except Exception as error:
        print("Error loading categories:", error)
        return []

    finally:
        con.close()


# ---------------------------------------------------------------------
# ADD CATEGORY
# ---------------------------------------------------------------------
def add_category(user_id, category_name, category_type):
    con = connect()

    if con is None:
        return

    try:
        cur = con.cursor()

        cur.execute("""
            INSERT INTO categories (name, type)
            VALUES (?, ?)
        """, (category_name, category_type.lower()))

        con.commit()

    except Exception as error:
        print("Error adding category:", error)

    finally:
        con.close()


# ---------------------------------------------------------------------
# DELETE CATEGORY
# ---------------------------------------------------------------------
def delete_category(category_id):
    con = connect()

    if con is None:
        return

    try:
        cur = con.cursor()

        cur.execute("""
            DELETE FROM categories
            WHERE id = ?
        """, (category_id,))

        con.commit()

    except Exception as error:
        print("Error deleting category:", error)

    finally:
        con.close()

# ---------------------------------------------------------------------
# ADD TRANSACTION
# Inserts a new transaction into database
# ---------------------------------------------------------------------
def add_transaction(
    user_id,
    transaction_type,
    category_name,
    amount,
    transaction_date,
    is_monthly
):

    # Connect to database
    con = connect()

    # Stop if connection failed
    if con is None:
        return

    try:
        # Create cursor
        cur = con.cursor()

        # Find category id
        cur.execute("""
            SELECT id
            FROM categories
            WHERE name = ?
            AND type = ?
        """, (
            category_name,
            transaction_type.lower()
        ))

        category = cur.fetchone()

        # Stop if category does not exist
        if category is None:
            return

        # Get category id
        category_id = category[0]

        # Insert transaction into database
        cur.execute("""
            INSERT INTO transactions
            (
                category_id,
                amount,
                date,
                is_monthly,
                created_by
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            category_id,
            amount,
            transaction_date,
            is_monthly,
            user_id
        ))

        # Save changes
        con.commit()

    except Exception as error:

        print("Error adding transaction:", error)

    finally:
        # Close connection
        con.close()


# ---------------------------------------------------------------------
# GET TRANSACTIONS
# Returns all user transactions
# ---------------------------------------------------------------------
def get_transactions(user_id):

    # Connect to database
    con = connect()

    # Return empty list if connection failed
    if con is None:
        return []

    try:
        # Create cursor
        cur = con.cursor()

        # Retrieve transactions
        cur.execute("""
            SELECT
                transactions.id,
                transactions.date,
                categories.type,
                categories.name,
                transactions.amount,
                transactions.is_monthly
            FROM transactions

            INNER JOIN categories
            ON transactions.category_id = categories.id

            WHERE transactions.created_by = ?

            ORDER BY transactions.date DESC
        """, (user_id,))

        # Return all results
        return cur.fetchall()

    except Exception as error:

        print("Error loading transactions:", error)

        return []

    finally:
        # Close connection
        con.close()


# ---------------------------------------------------------------------
# DELETE TRANSACTION
# Deletes transaction by ID
# ---------------------------------------------------------------------
def delete_transaction(transaction_id):

    # Connect to database
    con = connect()

    # Stop if connection failed
    if con is None:
        return

    try:
        # Create cursor
        cur = con.cursor()

        # Delete transaction
        cur.execute("""
            DELETE FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        # Save changes
        con.commit()

    except Exception as error:

        print("Error deleting transaction:", error)

    finally:
        # Close connection
        con.close()
