# games.py

# Add other import statements here as needed

import random
from tabulate import tabulate
from datetime import datetime, timedelta
from db import get_connection, get_cursor
from utils import print_seperator_tilda, print_seperator_star, print_error, print_info, print_table_header_seperator
from players import get_player_name
from sessions import get_session_id, get_games_played_last_session_id
from prettytable import PrettyTable, ALL


def select_teams(club_id, season_id, session_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Get players who are currently playing a game
            cur.execute("""
                SELECT DISTINCT unnest(array_cat(gv.team_1_player_ids, gv.team_2_player_ids))
                FROM games_view gv
                WHERE gv.session_id = %s AND gv.game_end_time IS NULL
            """, (session_id,))
            players_in_games = cur.fetchall()
            players_in_games_ids = [player[0] for player in players_in_games]

            # Get the total number of players in the club, excluding those already in games
            if players_in_games_ids:
                cur.execute("""
                    SELECT COUNT(*)
                    FROM sessions_players sp
                    JOIN sessions s ON sp.session_id = s.id
                    WHERE s.club_id = %s AND s.id = %s AND sp.player_id NOT IN %s
                """, (club_id, session_id, tuple(players_in_games_ids)))
            else:
                cur.execute("""
                    SELECT COUNT(*)
                    FROM sessions_players sp
                    JOIN sessions s ON sp.session_id = s.id
                    WHERE s.club_id = %s AND s.id = %s
                """, (club_id, session_id))

            num_players = cur.fetchone()[0]

            cur.execute("""SELECT option_value
                           FROM club_options
                           WHERE club_id = %s AND option_name = 'max_players_per_court'""",
                        (club_id,))
            max_players_per_court = cur.fetchone()[0]

            if num_players < int(max_players_per_court):
                print_error(f"Not enough players ({num_players}/{max_players_per_court}) for a game in this session ({session_id}).")
                return

            # Fetch the algorithm option from club_options table
            cur.execute("""SELECT option_value
                           FROM club_options
                           WHERE club_id = %s AND option_name = 'algorithm'""",
                        (club_id,))
            option_value = cur.fetchone()

            if option_value:
                algorithm = option_value[0]
            else:
                print("No algorithm found for this club.")
                return

            cur.execute("""SELECT players.id, players.name
                        FROM sessions_players
                        JOIN players ON sessions_players.player_id = players.id
                        WHERE session_id = %s AND active = 'Y'""", (session_id,))
            players = cur.fetchall()

            if algorithm == "random":
                select_teams_random(club_id, session_id, players)
            elif algorithm == "levels":
                select_teams_levels(club_id, session_id, players)
            else:
                print("Invalid algorithm option. Please set a valid algorithm for this club.")
                return




def select_teams_random(club_id, session_id, players):
    def get_recent_teammates(session_id,player_id):
        cur.execute("""
            SELECT DISTINCT tp2.player_id, g.game_start_time
            FROM games g
            JOIN teams_players tp1 ON (g.team1_id = tp1.team_id OR g.team2_id = tp1.team_id)
            JOIN teams_players tp2 ON (g.team1_id = tp2.team_id OR g.team2_id = tp2.team_id)
            WHERE g.session_id = %s AND tp1.player_id = %s AND tp2.player_id != %s
            ORDER BY g.game_start_time DESC
            LIMIT 5
        """, (session_id, player_id, player_id))
        return {row[0] for row in cur.fetchall()}

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Get the player IDs of players currently in a game
            cur.execute("""
                SELECT DISTINCT tp.player_id
                FROM games g
                JOIN teams_players tp ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
                WHERE g.session_id = %s AND g.game_end_time IS NULL
            """, (session_id,))
            ongoing_player_ids = {row[0] for row in cur.fetchall()}

            # Remove ongoing players from the available players list
            available_players = [player for player in players if player[0] not in ongoing_player_ids]

            # Get the number of games played by each player
            cur.execute("""
                SELECT sp.player_id, sp.played
                FROM sessions_players sp
                WHERE sp.session_id = %s
            """, (session_id,))
            games_played = {row[0]: row[1] for row in cur.fetchall()}

            # Sort available players by the number of games played (ascending)
            available_players.sort(key=lambda player: games_played[player[0]])

            selected_players = []
            for _ in range(2):
                for player in available_players:
                    player_id = player[0]
                    recent_teammates = get_recent_teammates(session_id, player_id)
                    
                    # Find a player who has not played with the current player recently
                    for potential_teammate in available_players:
                        if potential_teammate[0] != player_id and potential_teammate[0] not in recent_teammates:
                            break
                    else:
                        # If no such player is found, choose a random teammate
                        potential_teammate = random.choice([p for p in available_players if p[0] != player_id])

                    selected_players.append(player)
                    selected_players.append(potential_teammate)

                    # Remove the selected players from the available players list
                    available_players.remove(player)
                    available_players.remove(potential_teammate)

                    if len(selected_players) == 4:
                        break

                if len(selected_players) == 4:
                    break

            # ... (rest of the function remains unchanged)


            # Convert the selected players list of tuples into a list of player IDs
            player_ids = [player[0] for player in selected_players]

            # Get the player names for the given player IDs
            cur.execute("""SELECT id, name FROM players WHERE id IN %s""", (tuple(player_ids),))
            players_info = cur.fetchall()
            players_dict = {player_id: player_name for player_id, player_name in players_info}

            # Unpack the selected player names and IDs
            player1_id, player1_name = selected_players[0]
            player2_id, player2_name = selected_players[1]
            player3_id, player3_name = selected_players[2]
            player4_id, player4_name = selected_players[3]

            # Insert the teams
            cur.execute("""INSERT INTO teams DEFAULT VALUES RETURNING id""")
            team1_id = cur.fetchone()[0]

            cur.execute("""INSERT INTO teams_players (team_id, player_id) VALUES (%s, %s), (%s, %s)""",
                        (team1_id, player1_id, team1_id, player2_id))

            cur.execute("""INSERT INTO teams DEFAULT VALUES RETURNING id""")
            team2_id = cur.fetchone()[0]

            cur.execute("""INSERT INTO teams_players (team_id, player_id) VALUES (%s, %s), (%s, %s)""",
                        (team2_id, player3_id, team2_id, player4_id))

            # Insert the game
            cur.execute("""INSERT INTO games (session_id, team1_id, team2_id, game_start_time, team1_score, team2_score)
                            VALUES (%s, %s, %s, NOW(), 0, 0)
                            RETURNING id""",
                        (session_id, team1_id, team2_id))
            game_id = cur.fetchone()[0]

            conn.commit()

            print_info("New Game Created")
            print(f"Game ID: {game_id}")
            # Create and configure the table
            table = PrettyTable()
            table.field_names = ["Team No", "Team ID", "Player 1", "Player 2"]
            table.hrules = ALL  # Add horizontal rules between all rows

            # Add rows with team information
            table.add_row(["1", team1_id, player1_name, player2_name])
            table.add_row(["2", team2_id, player3_name, player4_name])

            # Print the table
            print(table)

            print_seperator_tilda()
            print(" ")

            return game_id, team1_id, team2_id



def select_teams_levels(club_id, season_id, session_id):
    # Add logic for team selection based on levels
    pass


def end_game(club_id: int, season_id: int, session_id: int):
    session_id = get_session_id(club_id, season_id)
    print(f"Club ID: {club_id}, Season ID: {season_id}, Session_ID: {session_id}")

    games = get_ongoing_games(session_id)

    if not games:
        print("No games in progress.")
        return

    while True:
        game_id = input("Enter Game ID to end game (Press 0 to exit): ")

        if game_id == '0':
            print("Exiting now.")
            break

        try:
            game_id = int(game_id)
        except ValueError:
            print_error("Invalid input. Please enter a number.")
            continue

        game = next((g for g in games if g[0] == game_id), None)
        if not game:
            print_error("Invalid Game ID. Please enter a valid Game ID.")
            continue

        team1_score = input("Enter team 1 score: ")
        team2_score = input("Enter team 2 score: ")

        try:
            team1_score = int(team1_score)
            team2_score = int(team2_score)
        except ValueError:
            print_error("Invalid input. Please enter a number.")
            continue
        if team1_score > team2_score:
            winning_team = game[1]  # team1_id
            losing_team = game[2]   # team2_id
        elif team1_score < team2_score:
            winning_team = game[2]  # team2_id
            losing_team = game[1]   # team1_id
        else:
            winning_team = None
            losing_team = None

        game_end_time = datetime.now()

        with get_connection() as conn:
            with get_cursor(conn) as cur:
                try:
                    cur.execute("""UPDATE games
                                    SET team1_score = %s, team2_score = %s, winner_team_id = %s,
                                        game_end_time = %s
                                    WHERE id = %s""",
                                (team1_score, team2_score, winning_team, game_end_time, game_id))

                    # Update the sessions_players table with the played, win, draw stats
                    if winning_team:
                        for player_id in get_team_player_ids(winning_team):
                            update_player_stats(player_id, session_id, 'win')
                        for player_id in get_team_player_ids(losing_team):
                            update_player_stats(player_id, session_id, 'lose')
                    else:
                        for player_id in get_team_player_ids(game[5]) + get_team_player_ids(game[6]):
                            update_player_stats(player_id, session_id, 'draw')

                except Exception as e:
                    print(f"Error: could not end game: {e}")
                    conn.rollback()
                else:
                    conn.commit()
                    print("Game ended successfully.")
                    break




def get_team(team_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT p1.id, p1.name, p2.id, p2.name
                            FROM teams_players tp1
                            INNER JOIN teams_players tp2 ON tp1.team_id = tp2.team_id AND tp1.player_id != tp2.player_id
                            INNER JOIN players p1 ON tp1.player_id = p1.id
                            INNER JOIN players p2 ON tp2.player_id = p2.id
                            WHERE tp1.team_id = %s""",
                        (team_id,))
            team = cur.fetchall()
            if not team:
                return None

            return team



def get_team_player_ids(team_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT player_id FROM teams_players WHERE team_id = %s""", (team_id,))
            result = cur.fetchall()
            return [row[0] for row in result]



def update_player_stats(player_id: int, session_id: int, result: str):
    if result not in ['win', 'lose', 'draw']:
        print_error("Cannot update player stats. Result should be 'win', 'lose', or 'draw'.")
        return
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            try:
                if result == 'win':
                    cur.execute("""UPDATE sessions_players
                                    SET played = played + 1, won = won + 1
                                    WHERE player_id = %s AND session_id = %s""",
                                (player_id, session_id))
                elif result == 'lose':
                    cur.execute("""UPDATE sessions_players
                                    SET played = played + 1
                                    WHERE player_id = %s AND session_id = %s""",
                                (player_id, session_id))
                elif result == 'draw':
                    cur.execute("""UPDATE sessions_players
                                    SET played = played + 1, draw = draw + 1
                                    WHERE player_id = %s AND session_id = %s""",
                                (player_id, session_id))

#                cur.execute("""UPDATE sessions_players
#                                SET win_percentage = 100 * won / played
#                                WHERE player_id = %s AND session_id = %s""",
#                            (player_id, session_id))

            except Exception as e:
                print_error(f"Could not update player stats: {e}")
                conn.rollback()
            else:
                conn.commit()
                #print(f"Player stats for player id {player_id} in session {session_id} updated successfully.")



def get_ongoing_games(session_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""
                SELECT gv.game_id,
                       gv.team_1,
                       gv.team_2,
                       p1.name AS player1_name,
                       p2.name AS player2_name,
                       p3.name AS player3_name,
                       p4.name AS player4_name,
                       gv.game_start_time
                FROM games_view gv
                JOIN players p1 ON gv.team_1_player_names[1] = p1.name
                JOIN players p2 ON gv.team_1_player_names[2] = p2.name
                JOIN players p3 ON gv.team_2_player_names[1] = p3.name
                JOIN players p4 ON gv.team_2_player_names[2] = p4.name
                WHERE gv.session_id = %s AND gv.game_end_time IS NULL
            """, (session_id,))
            print (f"session id : {session_id}")

            games = cur.fetchall()

            print_info("Ongoing Games")
            table = PrettyTable()
            table.field_names = ["ID", "Team 1", "Team 2", "Start Time"]
            table.align["Team 1"] = "l"  # Set left alignment for Team 1 column
            table.align["Team 2"] = "l"  # Set left alignment for Team 2 column
            for game in games:
                start_time = game[7].strftime("%H:%M")
                team1 = f"{game[3]}, {game[4]}"
                team2 = f"{game[5]}, {game[6]}"
                table.add_row([game[0], team1, team2, start_time])
            print(table)
            print_seperator_tilda()
            print(" ")
            return games




def set_options(club_id):
    pass
