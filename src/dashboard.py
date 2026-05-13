#Dashboard.py
#This py file will handle the dashboard section
#This is the entry point, all file paths will be guided from here
import sqlite3
import os
import logging #Logging will let us collect error logs from users
import tkinter as tk
from login_system import login
from database import database
from login_system import auth
#import GUI FILES
import config_and_styles as style


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
        #make the main window GUI (root)
        root = tk.Tk()
        root.title(style.APP_TITLE)
        root.geometry(style.APP_DIMENSIONS)
        
        con = database.connect() #connect to database
        if con:
            loged_in = auth.check_login() #check if user is loged in
            if (loged_in):
                #dashboardGUI(root)
                print("dashboard")
            else:
                login.build_login_gui(root)
                #login.start_login()
                #get current user (it will be only id when we have data from db
                #active_user = auth.get_user()
                #if active_user:
                    #print(f"Welcome {active_user.username} with id:{active_user.id}!!")
            
        else:
            print("There was a problem while creating the tables")
        #run the App
        root.mainloop()
            
    #if program crashes for other reason write to logfile
    except Exception as e:
        logging.exception("Critical Error: The application crashed")
#-------------------------------------------------------------------------

#start main if we are only at dashboard (run this if the file was executed directly)
if __name__ == "__main__":
    main()
    
#-------------------------------------------------------------------------
#GUI
def build_dashboard_gui(root):
    #Clear the login screen widgets
    for widget in root.winfo_children():
        widget.destroy()

    #Get the logged-in user data from auth
    active_user = auth.get_user()

    #Create the Dashboard Label
    dashboard_text = f"Welcome {active_user.username} (ID: {active_user.id})"
    
    lbl_welcome = tk.Label(
        root, 
        text=dashboard_text, 
        font=(style.FONT_FAMILY, style.FONT_SIZE_TITLE, "bold"),
        bg=style.COLOR_BG_MAIN,
        fg=style.COLOR_TEXT_MAIN
    )
    lbl_welcome.pack(pady=100)
    
