# players.py
from db import get_connection, get_cursor
from utils import print_seperator_tilda, print_error, print_info


def display_club_players(club_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT id, name
                           FROM players
                           WHERE id IN (SELECT player_id
                                        FROM players_clubs
                                        WHERE club_id = %s
                                          AND approved = true
                                          AND archived = false)
                           ORDER BY id""",
                        (club_id,))
            players = cur.fetchall()

            print (" ")
            print_seperator_tilda()
            print("Club Players:")
            for player in players:
                print(f"{player[0]}. {player[1]}")

            return players


def display_club_players_not_playing_today(club_id, session_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT id, name
                           FROM players
                           WHERE id IN (SELECT player_id
                                        FROM players_clubs
                                        WHERE club_id = %s
                                          AND approved = true
                                          AND archived = false)
                             AND id NOT IN (SELECT player_id
                                            FROM sessions_players
                                            WHERE session_id = %s AND active = 'Y')
                           ORDER BY id""",
                        (club_id, session_id))
            players = cur.fetchall()


            print_info("Club Players Available For Selection:")
            for player in players:
                print(f"{player[0]}. {player[1]}")

            return players


def display_club_players_playing_today(club_id, session_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT id, name
                           FROM players
                           WHERE id IN (SELECT player_id
                                        FROM players_clubs
                                        WHERE club_id = %s
                                          AND approved = true
                                          AND archived = false)
                             AND id IN (SELECT player_id
                                        FROM sessions_players
                                        WHERE session_id = %s AND active = 'Y')
                           ORDER BY id""",
                        (club_id, session_id))
            players = cur.fetchall()


            print_info("Club Players Playing Today:")
            for player in players:
                print(f"{player[0]}. {player[1]}")

            return players


def get_player_name(player_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT name FROM players WHERE id = %s", (player_id,))
            player_name = cur.fetchone()
            if player_name:
                return player_name[0]
            else:
                print_error("Player not found.")
                return None


