# seasons.py

from datetime import datetime
from db import get_connection, get_cursor
from utils import print_error, print_title, print_info

def get_season(club_id):
    today = datetime.now().date()
    now = datetime.now()

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT id FROM seasons WHERE club_id = %s
                           AND %s BETWEEN date_from AND date_to""",
                        (club_id, now.date()))
            season_id = cur.fetchone()

            if season_id:
                return season_id[0]  # Return the first element of the tuple
            else:
                print_error("No active season found for the club.")
                season_id = create_new_season(club_id)
                return season_id



def create_new_season(club_id):
    date_from = input("Enter season start date (YYYY-MM-DD): ")
    date_to = input("Enter season end date (YYYY-MM-DD): ")

    try:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        print_error("Invalid date format. Please enter dates in YYYY-MM-DD format.")
        return None

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            try:
                cur.execute("""INSERT INTO seasons (club_id, date_from, date_to)
                               VALUES (%s, %s, %s) RETURNING id""",
                            (club_id, date_from, date_to))
                season_id = cur.fetchone()[0]
                conn.commit()
                print_info("New season created")
                return season_id
            except Exception as e:
                print(f"Error creating new season: {e}")
                conn.rollback()
                return None