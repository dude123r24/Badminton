# login.py
 
import sys
from db import get_connection, get_cursor
from utils import print_error

global_player_id_logged_in = None

def login():
    global global_player_id_logged_in

    global_player_id_logged_in=1
    return True

    while True:
        email = input("Enter email (case insensitive) (Press 0 to exit): ")
        if email == '0':
            print("Exiting now.")
            sys.exit(0)
        
        password = input("Enter password (case sensitive): ")

        with get_connection() as conn:
            with get_cursor(conn) as cur:
                cur.execute("""SELECT id, name FROM players
                            WHERE lower(email) = lower(%s) AND password = %s""",
                            (email, password))
                player = cur.fetchone()

                if player:
                    global_player_id_logged_in = player[0]
                    global_player_name_logged_in = player[1]
                    print (" ")
                    print(f"Login successful. Welcome {global_player_name_logged_in}. Your player ID is {global_player_id_logged_in}")
                    return global_player_id_logged_in
                else:
                    print_error("Invalid email or password. Please try again or press 0 to exit.") 

