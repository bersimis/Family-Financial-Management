#Login.py
#This py file will handle the login section
import sqlite3
import logging
import hashlib # Added for password hashing verification
import tkinter as tk
import dashboard
from login_system import auth
from database import database
import config_and_styles as style

error_label = None # Set it as None globally
#-------------------------------------------------------------------------
def start_login(input_user,input_password, root):
    global error_label # Access the global label variable
    error_label.config(text="")
    
    #Here we will connect user by checking the right credentials after button click
    con = database.connect() #First we will connect to database
    
    username = input_user.get() #get string from widget
    password = input_password.get() #get string from widget
    
    # Check if fields are empty before database call
    if not username or not password:
        error_label.config(text="Please fill all fields") #error to show the user
        return
    
    if con:
        #make the cursor
        cur = con.cursor()
        
        try:
            # Hash the input password to compare it with the stored hash in the DB
            hashed_input = hashlib.sha256(password.encode()).hexdigest()

            #execute the query
            #We now compare the hashed_input with the hashed password in the database
            cur.execute("""
            SELECT id,username,role_id
                FROM users
                WHERE username=? AND password=?
            """, (username, hashed_input)) 

            #take result from query
            result = cur.fetchone()
            
            if result: #if result is not None
                #get result (its a tuple)
                correct_user_id = result[0]
                correct_username = result[1]
                correct_role_id = result[2]
                
                #send correct credentials to auth
                auth.set_user(correct_user_id, correct_username, correct_role_id)
                dashboard.build_dashboard_gui(root) # on corect credentials go to dashboard GUI
                
            else:
                error_label.config(text="Wrong credentials, try again") #error to show the user
                

        except Exception as e:
            logging.exception("An error occurred during login.")

        finally:
            #close the connection
            con.close()
            # Removed the show_error call as we now use error_label.config directly
#-------------------------------------------------------------------------
#GUI
def build_login_gui(root):
    global error_label #To handle errors
    #Set the global background for the main window
    root.configure(bg=style.COLOR_BG_MAIN)
    
    #Clear everything so we can show login GUI
    for widget in root.winfo_children():
        widget.destroy()

    #----------Now build the login GUI-----------
    #Title Label - Added bg and used FONT_FAMILY
    label = tk.Label(
        root, 
        text="Login", 
        font=(style.FONT_FAMILY, style.FONT_SIZE_TITLE, "bold"),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    )
    label.pack(pady=50)
    
    #---Username frame---
    #You MUST set bg=style.COLOR_BG_MAIN on the frame too!
    user_frame = tk.Frame(root, bg=style.COLOR_BG_MAIN)
    user_frame.pack(pady=10)

    user_label = tk.Label(
        user_frame, 
        text="Username:", 
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    )
    user_label.pack(side="left", padx=5)

    input_user = tk.Entry(
        user_frame, 
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        relief="solid",
        bd=1
    )
    input_user.pack(side="left", padx=5)
    
    #---Password frame---
    #Added bg to the frame
    password_frame = tk.Frame(root, bg=style.COLOR_BG_MAIN)
    password_frame.pack(pady=10)

    password_label = tk.Label(
        password_frame, 
        text="Password:", 
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    )
    password_label.pack(side="left", padx=5)

    input_password = tk.Entry(
        password_frame, 
        font=(style.FONT_FAMILY, style.FONT_SIZE_INPUT),
        show="*",
        relief="solid",
        bd=1
    )
    input_password.pack(side="left", padx=5)

    #---Submit Button---
    btn_login = tk.Button(
        root,
        text="LOGIN",
        font=(style.FONT_FAMILY, style.FONT_SIZE_BUTTON, "bold"),
        bg=style.COLOR_SUCCESS,
        fg=style.COLOR_LIGHT,
        width=15,
        command=lambda: start_login(input_user, input_password, root) #This calls your database function
    )
    btn_login.pack(pady=30)

#if we catch an error in login then we will show it here
    #---Error Label---
    error_label = tk.Label(
        root, 
        text="", 
        font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_ERROR
    )
    error_label.pack(pady=5)

    #---Register Link---
    from login_system import register
    register_link = tk.Label(
        root,
        text="Don't have an account? Register here",
        font=(style.FONT_FAMILY, style.FONT_SIZE_TEXT, "underline"),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_PRIMARY,
        cursor="hand2"
    )
    register_link.pack(pady=10)
    register_link.bind("<Button-1>", lambda event: register.build_register_gui(root))
    register_link.bind("<Enter>", lambda event: register_link.config(fg=style.COLOR_LINK_HOVER))
    register_link.bind("<Leave>", lambda event: register_link.config(fg=style.COLOR_PRIMARY))
