from tabulate import tabulate
from datetime import datetime, timedelta
from db import get_connection, get_cursor
from utils import print_seperator_tilda, print_seperator_star, print_error, print_info, print_table_header_seperator
from sessions import get_session_id, get_games_played_last_session_id

def report_player_stats_by_session(club_id, season_id):
    session_id = input("Enter session ID (leave blank to get last session ID): ").strip()

    if not session_id:
        session_id = get_games_played_last_session_id(club_id)
    else:
        with get_connection() as conn:
            with get_cursor(conn) as cur:
                cur.execute("""
                    SELECT id FROM sessions
                    WHERE club_id = %s AND season_id = %s AND id = %s
                """, (club_id, season_id, session_id))
                if not cur.fetchone():
                    print_error(f"No games were played for this session ({session_id}) for this club.")
                    return

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Get player session stats for the selected session_id
            cur.execute("""SELECT player_name, played, won, (played - won - draw) lost, win_percentage, avg_victory_margin, minutes_since_last_game, session_rank
                        FROM player_stats_by_session
                        WHERE session_id = %s""",
                        (session_id,))
            player_stats = cur.fetchall()

            # Print results in tabular format
            print (" ")
            print_table_header_seperator(140)
            print("\033[1m{:<20} {:<15} {:<15} {:<15} {:<20} {:<20} {:<20} {:<20}\033[0m".format(
                "Player", "Games Played", "Games Won", "Games Lost", "Win Percentage", "Avg Victory Margin", "Mins, Last Game", "Rank"
            ))
            print_table_header_seperator(140)

            for stats in player_stats:
                # Replace None values with empty strings
                stats = tuple('' if value is None else value for value in stats)
                print("{:<20} {:<15} {:<15} {:<15} {:<20} {:<20} {:<20} {:<20}".format(*stats))



def report_session_games_played(club_id, season_id):

    session_id = input("Enter session ID (leave blank to get last session ID): ").strip()

    if not session_id:
        session_id = get_games_played_last_session_id(club_id)
    else:
        with get_connection() as conn:
            with get_cursor(conn) as cur:
                cur.execute("""
                    SELECT id FROM sessions
                    WHERE club_id = %s AND season_id = %s AND id = %s
                """, (club_id, season_id, session_id))
                if not cur.fetchone():
                    print_error(f"No games were played for this session ({session_id}) for this club.")
                    return

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Get games played for the selected session_id
            cur.execute("""SELECT gv.game_id, gv.game_start_time, 
                                  array_to_string(gv.team_1_player_names, ' & ') AS team1_players,
                                  array_to_string(gv.team_2_player_names, ' & ') AS team2_players,
                                  winner.name || ' & ' || winner_partner.name AS winning_team,
                                  EXTRACT(MINUTE FROM (gv.game_end_time - gv.game_start_time)) AS duration
                           FROM games_view gv
                           JOIN (SELECT team_id, player_id, ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY player_id) AS rn FROM teams_players) AS winning_team_player1 ON gv.winning_team = winning_team_player1.team_id AND winning_team_player1.rn = 1
                           JOIN players AS winner ON winning_team_player1.player_id = winner.id
                           JOIN (SELECT team_id, player_id, ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY player_id) AS rn FROM teams_players) AS winning_team_player2 ON gv.winning_team = winning_team_player2.team_id AND winning_team_player2.rn = 2
                           JOIN players AS winner_partner ON winning_team_player2.player_id = winner_partner.id
                           WHERE gv.session_id = %s AND EXISTS (SELECT 1 FROM sessions WHERE id = gv.session_id AND club_id = %s)
                           ORDER BY gv.game_start_time ASC
                        """, (session_id, club_id))
            games_played = cur.fetchall()

            # Print results in tabular format
            print(" ")
            print_table_header_seperator(150)
            print("\033[1m{:<8} {:<20} {:<35} {:<35} {:<35} {:<20}\033[0m".format(
                "Game ID", "Date & Time", "Team 1", "Team 2", "Winner", "Duration (min)"
            ))
            print_table_header_seperator(150)

            for game in games_played:
                game_id, date_time, team1_players, team2_players, winning_team, duration = game
                date_time_str = date_time.strftime("%Y-%m-%d %H:%M")
                print("{:<8} {:<20} {:<35} {:<35} {:<35} {:<20}".format(
                    game_id, date_time_str, team1_players, team2_players, winning_team, duration
                ))


def report_session_player_games_played(club_id, session_id):
    pass