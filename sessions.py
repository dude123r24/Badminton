# sessions.py
import sys
from datetime import datetime, date
from db import get_connection, get_cursor
from players import display_club_players, display_club_players_not_playing_today, display_club_players_playing_today
from psycopg2.errors import UniqueViolation
from utils import print_error, print_seperator_plus, print_info
from seasons import get_season, create_new_season




def end_session_for_player(club_id, session_id):
    while True:
        players_playing_today = display_club_players_playing_today(club_id, session_id)
        if not players_playing_today:
            print_error("No players are playing today.")
            return

        print (" ")
        print("Select a player ID to end their session or press ENTER to finish:")
        user_input = input()
        if user_input.strip() == "":
            break

        try:
            player_id = int(user_input)
        except ValueError:
            print_error("Invalid input. Please enter a valid player ID or press ENTER to return.")
            continue

        if not any(player[0] == player_id for player in players_playing_today):
            print_error("Invalid player ID. Please select a player ID from the list.")
            continue

        with get_connection() as conn:
            with get_cursor(conn) as cur:
                cur.execute("""SELECT COUNT(*)
                               FROM games
                               WHERE session_id = %s
                                 AND (team1_id IN (SELECT team_id FROM teams_players WHERE player_id = %s) OR
                                      team2_id IN (SELECT team_id FROM teams_players WHERE player_id = %s))
                                 AND winner_team_id IS NULL""",
                            (session_id, player_id, player_id))
                ongoing_games_count = cur.fetchone()[0]

                if ongoing_games_count > 0:
                    print_error(f"Player {player_id} is currently involved in ongoing games. Please finish the games before ending the session for the player.")
                    return None

                cur.execute("""UPDATE sessions_players
                               SET active = 'N'
                               WHERE session_id = %s AND player_id = %s""",
                            (session_id, player_id))
                conn.commit()

        print_info(f"Player {player_id} has been removed from the session.")
        break

# Select which players are playing in today's session
def sessions_players_select(club_id, season_id, session_id):
    players_playing = display_club_players_playing_today (club_id, session_id)

    players = display_club_players_not_playing_today (club_id, session_id)

    print (" ")
    print("Select players playing today:")
    playing_today = []
    while True:
        player_id = input("Enter player ID (or '0' to finish): ")
        if player_id.strip() == "":
            break
        if player_id.lower() == '0':
            break

        try:
            player_id = int(player_id)
        except ValueError:
            print_error ("Invalid input. Please enter a valid player ID or '0' to finish.")
            continue

        player = next((player for player in players if player[0] == player_id), None)
        if player:
            if player_id not in playing_today:
                playing_today.append(player_id)
                print(f"Selected player: {player[1]}")
            else:
                print("Player already selected.")
        else:
            print_error ("Player not found. Please enter a valid player ID.")

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            for player_id in playing_today:
                try:
                    cur.execute("""INSERT INTO sessions_players (session_id, player_id, active)
                                   VALUES (%s, %s, 'Y')""",
                                (session_id, player_id))
                except UniqueViolation as e:
                    print_error (f"Cannot add. Player {player_id} is already added to the session players.")
                    #print(f"Error: Cannot add. Player {player_id} is already added to the session players.")
                    conn.rollback()
                    continue
                except Exception as e:
                    print(f"Error: cannot add player {player_id} to session players: {e}")
                    conn.rollback()
                    continue
                else:
                    conn.commit()


    print("Players playing today:")
    for player_id in playing_today:
        player = next(player for player in players if player[0] == player_id)
        print(f"{player_id}. {player[1]}")


# Create a session
def create_session(club_id):
    now = datetime.now()

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Get the season for the club that is active today
            season_id = get_season(club_id)

            # If there is no active season for the club, create one
            if not season_id:
                print("No active season found for the club. Creating new season.")
                season_id = create_new_season(club_id)

            # Check if a session already exists for today's date
            cur.execute("""SELECT id FROM sessions WHERE club_id = %s AND session_date = %s""",
                        (club_id, now.date()))
            existing_session = cur.fetchone()

            # If session already exists for today's date, return the existing session id
            if existing_session:
                return existing_session[0]

            # Get number of courts and players per court from club options
            cur.execute("""SELECT option_name, option_value FROM club_options
                           WHERE club_id = %s AND (option_name = 'num_courts' OR option_name = 'max_players_per_court')""",
                        (club_id,))
            options = dict(cur.fetchall())

            # Check if options are found in club_options
            if 'num_courts' not in options or 'max_players_per_court' not in options:
                print_error("Cannot create session. Club options are missing. Please contact amit2u@hotmail.com to resolve this issue.")
                sys.exit()
                return None

            # Insert new session
            cur.execute("""INSERT INTO sessions (club_id, season_id, session_date, no_of_courts, no_of_players_per_court)
                           VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                           (club_id, season_id, now.date(), options['num_courts'], options['max_players_per_court']))
            session_id = cur.fetchone()[0]
            conn.commit()

    return session_id


def check_session_has_players(club_id, session_id):
    # Your implementation
    pass


def get_session_id(club_id, season_id):
    """Check if there is already a session going on for the given club and season on today's date"""

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""
                SELECT id FROM sessions
                WHERE club_id = %s AND season_id = %s AND session_date = current_date
            """, (club_id, season_id))
            session = cur.fetchone()
            if session:
                return session[0]
            else:
                return None


def get_games_played_last_session_id(club_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""
                SELECT MAX(g.session_id) 
                FROM games g 
                JOIN sessions s ON g.session_id = s.id 
                WHERE s.club_id = %s
            """, (club_id,))
            last_session = cur.fetchone()[0]
            return last_session




'''
Add error handling: In some of your functions, such as create_session, you could add additional error handling to ensure that the function works as intended, even if unexpected errors occur.
Refactor code: You could refactor some of your code to reduce duplication and improve readability. For example, the display_club_players_playing_today and display_club_players_not_playing_today functions share some common functionality. You could consider creating a separate function to handle this functionality and call it from both functions.
Improve function names: Some of your function names could be improved to more accurately describe what the function does. For example, get_session_id could be renamed to get_current_session_id to make it clear that it is checking for the current session.
Add comments: Add comments to your functions to explain what they do and how they work. This will help other developers understand your code and make changes more easily.
Consider using a Python ORM: You could consider using an Object Relational Mapper (ORM) such as SQLAlchemy to simplify interactions with the database and improve code readability.
'''