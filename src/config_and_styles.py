#config_and_styles.py
#here we will store GUI information about dimentions and styles, colors etc

#Using Bootstrap 5 palette
#More info here : https://getbootstrap.com/docs/5.0/utilities/colors/ 

# ------- CONFIGURATION -------
APP_TITLE = "Family Financial Management"
APP_DIMENSIONS = "1024x768"

# ----------- STYLES ----------
#Background Colors
COLOR_BG_MAIN = "#f8f9fa"     #Bootstrap 'Light' background
COLOR_BG_CARD = "#ffffff"     #Pure white for containers/cards

# Text Colors
COLOR_TEXT_MAIN = "#212529"   #Bootstrap 'Dark' for primary text
COLOR_TEXT_MUTED = "#6c757d"  #Bootstrap 'Muted' for secondary info

#Action Colors
COLOR_PRIMARY = "#0d6efd"     #Bootstrap 'Blue'
COLOR_LINK_HOVER = "#0a58ca"  #Bootstrap 'Dark Blue' on hover
COLOR_SUCCESS = "#198754"     #Bootstrap 'Green'
COLOR_DANGER  = "#dc3545"     #Bootstrap 'Red'
COLOR_LIGHT   = "#f8f9fa"     #White-ish for text on dark buttons

#Common used
COLOR_ERROR = COLOR_DANGER #used for displaying errors

#Fonts Settings
FONT_FAMILY = "Arial"
FONT_SIZE_TITLE = 32
FONT_SIZE_TEXT = 12
FONT_SIZE_BUTTON = 13
FONT_SIZE_INPUT = 14
