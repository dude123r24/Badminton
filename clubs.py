# clubs.py
from db import get_connection, get_cursor
from utils import print_seperator_tilda, print_error, print_title

def display_clubs():
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT id, name, city, country FROM clubs ORDER BY id")
            clubs = cur.fetchall()

            print_title("Clubs")
            for club in clubs:
                print(f"{club[0]}. {club[1]} ({club[2]}, {club[3]})")
            print("Press enter to exit")
            
def set_club(club_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT name FROM clubs WHERE id = %s", (club_id,))
            club_name = cur.fetchone()

            if club_name:
                return club_name[0]
            else:
                print_error("Invalid club ID.")
                return None

def display_club_owner_details(club_id, session_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT p.id, p.name, p.email, p.phone
                           FROM players p
                           JOIN clubs c ON p.id = c.created_by
                           WHERE c.id = %s""", (club_id,))
            owner_details = cur.fetchone()

            if owner_details:
                print_title("Club Owner Details")
                print("Club Owner Details")
                print("ID:", owner_details[0])
                print("Name:", owner_details[1])
                print("Email:", owner_details[2])
                print("Phone:", owner_details[3])
            else:
                print("No owner details found for the club.")