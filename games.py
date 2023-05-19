# games.py

# Add other import statements here as needed

import random
from tabulate import tabulate
from datetime import datetime, timedelta
from db import get_connection, get_cursor
from utils import print_seperator_tilda, print_seperator_star, print_error, print_info, print_table_header_seperator
from players import get_player_name
from sessions import get_session_id, get_games_played_last_session_id, players_playing_today 
from prettytable import PrettyTable, ALL
from reports import report_session_games_played



def select_teams_levels(club_id, season_id, session_id):
    # Add logic for team selection based on levels
    pass


def print_game(game_id, team1_id, team2_id, team1_player_ids, team2_player_ids):
# print_game: This function prints the NEW game created information including the game ID, team IDs, and player names for each team.
# Returns nothing
    # Get the player names for each team
    team1_players = get_player_names(team1_player_ids)
    team2_players = get_player_names(team2_player_ids)

    # Create a PrettyTable object for each team
    team1_table = PrettyTable(['Player ID', 'Player Name'])
    team2_table = PrettyTable(['Player ID', 'Player Name'])

    # Concatenate the player names with commas
    team1_player_names = ', '.join(team1_players)
    team2_player_names = ', '.join(team2_players)

    # Print the game info
    print_info("New Game Created")

    # Create a PrettyTable object
    game_table = PrettyTable(['ID', 'Team 1', 'Team 2'])
    # Add the game info to the table
    game_table.add_row([game_id, team1_player_names, team2_player_names])

    # Print the game info
    print(game_table)


# To print all players playing today and their wait times and number of games played
def print_all_players_info(session_id):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""
                SELECT sp.player_id, p.name, COUNT(g.id) as games_played, MAX(g.game_end_time) as last_game_end_time
                FROM sessions_players sp
                JOIN players p ON sp.player_id = p.id
                LEFT JOIN games g ON (g.team1_id IN (SELECT tp.team_id FROM teams_players tp WHERE tp.player_id = sp.player_id)
                                       OR g.team2_id IN (SELECT tp.team_id FROM teams_players tp WHERE tp.player_id = sp.player_id))
                                       AND g.session_id = %s
                WHERE sp.session_id = %s
                GROUP BY sp.player_id, p.name
                ORDER BY p.name
            """, (session_id, session_id))
            result = cur.fetchall()
    print("All players playing today:")
    table = PrettyTable(["ID", "Name", "Games Played", "Wait Time"])
    for row in result:
        player_id, name, games_played, last_game_end_time = row
        wait_time = datetime.now() - last_game_end_time if last_game_end_time else timedelta.max
        wait_time_str = f"{wait_time.total_seconds():.0f}s" if wait_time != timedelta.max else "N/A"
        table.add_row([player_id, name, games_played, wait_time_str])
    print(table)


def get_recent_teammates_and_wait_time(club_id, session_id, player_id):
# get_recent_teammates_and_wait_time: This function retrieves the recent teammates and wait time for a player in a specific club session.
# Returns a set of player IDs representing recent teammates and the total wait time in seconds.
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Get the IDs of all games played in the session by the player
            cur.execute("""
                SELECT DISTINCT g.id
                FROM games g
                JOIN teams_players tp ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
                WHERE g.session_id = %s AND tp.player_id = %s
            """, (session_id, player_id))
            recent_game_ids = [row[0] for row in cur.fetchall()]

            # If there are no recent games, return an empty set of teammates and maximum wait time
            if not recent_game_ids:
                return set(), timedelta.max.total_seconds()

            # Get the player IDs and game start times of games played in the session by the player
            cur.execute("""
                SELECT tp.player_id, g.game_start_time
                FROM games g
                JOIN teams_players tp ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
                WHERE g.id IN %s AND tp.player_id != %s
                ORDER BY g.game_start_time ASC
                LIMIT 4
            """, (tuple(recent_game_ids), player_id))
            recent_teammate_info = cur.fetchall()

            # Get the last game end time
            cur.execute("""
                SELECT MAX(g.game_end_time)
                FROM games g
                JOIN teams_players tp ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
                WHERE tp.player_id = %s AND g.session_id = %s
            """, (player_id, session_id))
            last_game_end_time = cur.fetchone()[0]
            wait_time = datetime.now() - last_game_end_time if last_game_end_time else timedelta.max

            return {row[0] for row in recent_teammate_info}, wait_time.total_seconds()



def get_player_names(player_ids):
# get_player_names: This function retrieves the names of players based on their IDs.
# Returns a list of player names.
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""
                SELECT name
                FROM players
                WHERE id IN %s
            """, (tuple(player_ids),))
            player_names = [row[0] for row in cur.fetchall()]
    return player_names



def get_games_played(player_id):
# get_games_played: This function retrieves the number of games played by a player.
# Returns the count of games played as an integer.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(g.id)
                FROM games g
                JOIN teams_players tp ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
                WHERE tp.player_id = %s
            """, (player_id,))
            return cur.fetchone()[0]


def get_ongoing_players(session_id):
# get_ongoing_players: This function retrieves the player IDs of players who are currently involved in ongoing games within a specific session.
# Returns a set of player IDs.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT tp.player_id
                FROM games g
                JOIN teams_players tp ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
                WHERE g.session_id = %s AND g.game_end_time IS NULL
            """, (session_id,))
            result = {row[0] for row in cur.fetchall()}
            return result
        
        
def get_ongoing_players_with_names(session_id):
# get_ongoing_players_with_names: This function retrieves the player IDs and names of players who are currently not involved in any ongoing games within a specific session.
# Returns a list of tuples, where each tuple contains a player ID and name.
    with get_connection() as conn:
        with conn.cursor() as cur:
            # First, fetch all players associated with the session
            cur.execute("""
                SELECT DISTINCT sp.player_id, p.name
                FROM sessions_players sp
                JOIN players p ON p.id = sp.player_id
                WHERE sp.session_id = %s
            """, (session_id,))
            session_players = {row[0]: row[1] for row in cur.fetchall()}

            # Next, fetch all players currently in a game
            cur.execute("""
                SELECT DISTINCT tp.player_id
                FROM games g
                JOIN teams_players tp ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
                WHERE g.session_id = %s AND g.game_end_time IS NULL
            """, (session_id,))
            ongoing_players = {row[0] for row in cur.fetchall()}

            # Subtract ongoing_players from session_players to get available players
            available_players = {player_id: name for player_id, name in session_players.items()
                                 if player_id not in ongoing_players}
            return list(available_players.items())



def create_team_and_associate_players(session_id, player_ids):
# create_team_and_associate_players: This function creates a team for a specific session and associates multiple players with the team.
# Returns the ID of the created team as an integer.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO teams (session_id)
                VALUES (%s)
                RETURNING id
            """, (session_id,))
            team_id = cur.fetchone()[0]

            for player_id in player_ids:
                cur.execute("""
                    INSERT INTO teams_players (team_id, player_id)
                    VALUES (%s, %s)
                """, (team_id, player_id))
            conn.commit()
            return team_id


def create_game(session_id, team1_id, team2_id, game_selection):
# create_game: This function creates a game within a specific session, assigning team IDs and a game selection.
# Returns the ID of the created game as an integer.
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""
                INSERT INTO games (session_id, team1_id, team2_id, team1_score, team2_score, game_start_time, game_selection)
                VALUES (%s, %s, %s, 0, 0, NOW(), %s)
                RETURNING id
            """, (session_id, team1_id, team2_id, game_selection.lower()))
            conn.commit()
            return cur.fetchone()[0]


def get_team(team_id):
# get_team: This function retrieves the team members of a specific team based on the team ID.
# Input: team_id (int) - The ID of the team.
# Return: Returns a list of tuples where each tuple contains the player ID and player name for two team members.
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
# get_team_player_ids: This function retrieves the player IDs associated with a specific team.
# Input: team_id (int) - The ID of the team.
# Return: Returns a list of player IDs.
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT player_id FROM teams_players WHERE team_id = %s""", (team_id,))
            result = cur.fetchall()
            return [row[0] for row in result]


def update_player_stats(player_id: int, session_id: int, result: str):
# update_player_stats: This function updates the statistics of a player in a specific session based on the game result.
# Input: player_id (int) - The ID of the player.
#        session_id (int) - The ID of the session.
#        result (str) - The result of the game ('win', 'lose', or 'draw').
# Return: Returns nothing.
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

            except Exception as e:
                print_error(f"Could not update player stats: {e}")
                conn.rollback()
            else:
                conn.commit()
                #print(f"Player stats for player id {player_id} in session {session_id} updated successfully.")



def get_ongoing_games(session_id):
# get_ongoing_games: This function retrieves the ongoing games within a specific session. Also prints the ongoing games in a formatted table.
# Input: session_id - The ID of the session.
# Return: Returns a list of tuples, where each tuple contains the game ID, team 1 ID, team 2 ID, player names for both teams, and game start time.
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

            games = cur.fetchall()

            print_info("Ongoing Games")
            table = PrettyTable()
            table.field_names = ["#", "Team 1", "Team 2", "Start Time"]
            table.align["Team 1"] = "l"  # Set left alignment for Team 1 column
            table.align["Team 2"] = "l"  # Set left alignment for Team 2 column
            for idx, game in enumerate(games, start=1):
                start_time = game[7].strftime("%H:%M")
                team1 = f"{game[3]}, {game[4]}"
                team2 = f"{game[5]}, {game[6]}"
                table.add_row([idx, team1, team2, start_time])
            print(table)
            print_seperator_tilda()
            print(" ")
            return games



def game_exists(game_id):
# game_exists: This function checks if a game with the specified game ID exists.
# Input: game_id (int) - The ID of the game.
# Return: Returns True if the game exists, False otherwise.
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""SELECT COUNT(*) FROM games WHERE id = %s""", (game_id,))
            return cur.fetchone()[0] == 1



def set_options(club_id):
    pass


def modify_a_game_score ():
    pass




def delete_played_game(club_id, season_id):
# delete_played_game: This function allows the user to delete a played game within a specific club and season. It then deletes the game from the database and updates player statistics accordingly.
# Input: club_id (int) - The ID of the club.
#        season_id (int) - The ID of the season.
# Return: Returns nothing.

    # Get the list of games played today
    try:
        report_session_games_played(club_id, season_id)
    except TypeError:
        print_info("No games were played for this session.")
        return

    # Get the game ID to delete
    while True:
        game_id_input = input("Enter game ID to delete (or press enter to go back): ")
        if game_id_input == "" or game_id_input == "0":
            return
        try:
            game_id = int(game_id_input)
            if not game_exists(game_id):
                print_error("Invalid game ID. Please enter a valid game ID.")
                continue
            break
        except ValueError:
            print_error("Invalid game ID. Please enter a valid game ID.")

    # Get the game details
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            try:
                cur.execute("""SELECT session_id, team_1, team_2, team_1_score, team_2_score, winning_team, team_1_player_names, team_2_player_names, game_start_time, game_end_time
                                FROM games_view
                                WHERE game_id = %s""",
                            (game_id,))
                game = cur.fetchone()
            except UndefinedColumn:
                cur.execute("""SELECT team1_id, team2_id, team1_score, team2_score
                                FROM games
                                WHERE id = %s""",
                            (game_id,))
                game = cur.fetchone()

    session_id = game[0]
    team_1_id = game[1]
    team_2_id = game[2]
    team_1_score = game[3]
    team_2_score = game[4]
    winning_team_id = game[5]
    team_1_player_names = game[6]
    team_2_player_names = game[7]
    game_start_time = game[8]
    game_end_time = game[9]
    if team_2_score == team_1_score:
        draw = 'yes'
    else: 
        draw = 'no'
                
    # Confirm deletion
    print(f"Are you sure you want to delete game {game_id}? (y/n)")
    choice = input().lower()
    if choice != "y":
        return

    # Delete the game
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("""DELETE FROM games WHERE id = %s""", (game_id,))


            # Update player stats
            if draw == 'yes':
                 # Update sessions_players for a draw
                cur.execute("""UPDATE sessions_players sp
                                SET played = played - 1, draw = draw -1
                                WHERE sp.session_id = %s AND sp.player_id IN (
                                    SELECT tp.player_id
                                    FROM teams_players tp
                                    WHERE tp.team_id IN (%s, %s)
                                )""",
                            (session_id, team_1_id, team_2_id))
            else:
                cur.execute("""UPDATE sessions_players sp
                                SET played = played - 1
                                WHERE sp.session_id = %s AND sp.player_id IN (
                                    SELECT tp.player_id
                                    FROM teams_players tp
                                    WHERE tp.team_id IN (%s, %s)
                                )""",
                            (session_id, team_1_id, team_2_id))
                
                # Update sessions_players for winning players
                cur.execute("""UPDATE sessions_players sp
                                SET won = won - 1
                                WHERE sp.session_id = %s AND sp.player_id IN (
                                    SELECT tp.player_id
                                    FROM teams_players tp
                                    WHERE tp.team_id = %s
                                )""",
                            (session_id, winning_team_id))
        conn.commit()
    print_info("Game deleted successfully!")


def select_game_manually(session_id):
# select_game_manually: This function allows the user to manually select players and create a game. This function interacts with the user to select players for Team 1 and Team 2, creates teams, and creates a game using the selected teams.
# Input: session_id (int) - The ID of the session.
# Return: Returns nothing.

    # Fetch the list of available players
    available_players = get_ongoing_players_with_names(session_id)

    # If less than 4 players are available, we cannot create a game
    if len(available_players) < 4:
        print_error("Not enough players for a game.")
        return

    print_info("Available Players")
    table = PrettyTable()
    table.field_names = ["ID", "Player Name"]
    for player in available_players: # change here
        table.add_row([player[0], player[1]])
    print(table)
    print_seperator_tilda()
    print(" ")

    team1 = []
    team2 = []

    remaining_players = available_players.copy()

    while len(team1) < 2:
        player_id = input("Enter Player ID to add to Team 1 (Press 0 to exit): ")
        if player_id == '0':
            print("Exiting now.")
            return
        try:
            player_id = int(player_id)
        except ValueError:
            print_error("Invalid input. Please enter a number.")
            continue

        # Find the player with this player_id in the list of remaining players
        player = next((player for player in remaining_players if player[0] == player_id), None)
        if player is None:
            print_error("Invalid player ID. Please enter a valid player ID.")
            continue

        remaining_players.remove(player)
        team1.append(player)

    available_players = remaining_players.copy()

    # Reprint the updated list
    print_info("Available Players")
    table = PrettyTable()
    table.field_names = ["ID", "Player Name"]
    for player in available_players: # change here
        table.add_row([player[0], player[1]])
    print(table)
    print_seperator_tilda()
    print(" ")

    while len(team2) < 2:
        player_id = input("Enter Player ID to add to Team 2 (Press 0 to exit): ")
        if player_id == '0':
            print("Exiting now.")
            return
        try:
            player_id = int(player_id)
        except ValueError:
            print_error("Invalid input. Please enter a number.")
            continue

        # Find the player with this player_id in the list of remaining players
        player = next((player for player in remaining_players if player[0] == player_id), None)
        if player is None:
            print_error("Invalid player ID. Please enter a valid player ID.")
            continue

        remaining_players.remove(player)
        team2.append(player)

    # Now, we have the teams ready. We can insert these teams into the database.

    team1_id = create_team_and_associate_players(session_id, [player[0] for player in team1])
    team2_id = create_team_and_associate_players(session_id, [player[0] for player in team2])

    game_id = create_game(session_id, team1_id, team2_id, 'manual')
    if game_id is None:
        print_error("Could not create game")
        return
    print_game(game_id, team1_id, team2_id, [player[0] for player in team1], [player[0] for player in team2])



def select_teams(club_id, season_id, session_id):
# select_teams: This function selects teams based on the specified algorithm (random or levels) for a given club, season, and session.
# Input: club_id (int) - The ID of the club.
#        season_id (int) - The ID of the season.
#        session_id (int) - The ID of the session.
# Return: Returns nothing.

# Note: This function retrieves the players currently playing a game and the total number of players in the club.
# It fetches the maximum players per court option from the club_options table and checks if there are enough players for a game.
# It also fetches the algorithm option from the club_options table and selects teams based on the specified algorithm (random or levels).
# If no valid algorithm is found, an error message is printed.
# The function calls the respective algorithm functions (select_teams_random or select_teams_levels) to select the teams.
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
                # select_teams_random(club_id, session_id, players)
                select_teams_fair(club_id, session_id, players)

            elif algorithm == "levels":
                select_teams_levels(club_id, session_id, players)
            else:
                print("Invalid algorithm option. Please set a valid algorithm for this club.")
                return


def select_teams_fair(club_id, session_id, players):
# select_teams_fair: This function selects teams fairly based on player availability, recent teammates, and wait times.
# Input: club_id (int) - The ID of the club.
#        session_id (int) - The ID of the session.
#        players (list) - List of available players.
# Return: Returns nothing.

# Note: This function first fetches the ongoing players and available players. It then sorts the available players based on wait time and random tiebreaker.
# The function selects the first player and chooses the second player from the remaining players excluding the recent teammates of the first player.
# It then selects the third player excluding the recent teammates of the first and second players. If no suitable third player is found, it chooses the player with the highest wait time.
# Finally, it selects the fourth player from the remaining players excluding the recent teammates of the third player. If no suitable fourth player is found, it chooses the player with the highest wait time.
# The selected players are used to create teams and a game using the create_team_and_associate_players and create_game functions, respectively.
# The game information is printed using the print_game function.
    print_all_players_info(session_id)

    ongoing_player_ids = get_ongoing_players(session_id)
    available_players = [player for player in players if player[0] not in ongoing_player_ids]

    games_played = {player[0]: get_games_played(player[0]) for player in available_players}
    recent_teammates_and_wait_times = {player[0]: get_recent_teammates_and_wait_time(club_id, session_id, player[0]) for player in available_players}

    # Filter players to ensure they don't play together in a team more than twice before playing with most other players
    filtered_players = []
    for player in available_players:
        player_id = player[0]
        teammate_ids = list(recent_teammates_and_wait_times[player_id][0])
        if teammate_ids:
            teammate_counts = [teammate_ids.count(teammate_id) for teammate_id in teammate_ids]
            max_count = max(teammate_counts)
            if max_count < len(teammate_ids) - 1:
                filtered_players.append(player)
        else:
            filtered_players.append(player)

    # Sort available players by wait time (descending) and in case of a tie, choose randomly
    available_players_sorted = sorted(filtered_players, key=lambda player: (-recent_teammates_and_wait_times.get(player[0])[1], random.random()))

    # Select players for teams
    first_player = available_players_sorted.pop(0)
    first_player_recent_teammates = list(recent_teammates_and_wait_times.get(first_player[0])[0])[:3]

    second_player = next((player for player in available_players_sorted if player[0] not in first_player_recent_teammates), None)
    if second_player:
        available_players_sorted.remove(second_player)

    third_player_recent_teammates = set(first_player_recent_teammates)
    if second_player:
        third_player_recent_teammates.update(list(recent_teammates_and_wait_times.get(second_player[0])[0]))

    third_player = next((player for player in available_players_sorted if player[0] not in third_player_recent_teammates), None)
    if not third_player:
        third_player = max(available_players_sorted, key=lambda player: recent_teammates_and_wait_times.get(player[0])[1], default=None)

    if third_player:
        available_players_sorted.remove(third_player)

    fourth_player = next((player for player in available_players_sorted if player[0] not in list(recent_teammates_and_wait_times.get(third_player[0])[0])), None)
    if not fourth_player:
        fourth_player = max(available_players_sorted, key=lambda player: recent_teammates_and_wait_times.get(player[0])[1], default=None)

    if fourth_player:
        available_players_sorted.remove(fourth_player)

    # Now, you have your selected players
    selected_players = [first_player, second_player, third_player, fourth_player]

    # Make sure all selected players are not None before proceeding to create teams and game
    if all(selected_players):
        selected_player_ids = [player[0] for player in selected_players]

        team1_id = create_team_and_associate_players(session_id, selected_player_ids[:2])
        team2_id = create_team_and_associate_players(session_id, selected_player_ids[2:])
        game_id = create_game(session_id, team1_id, team2_id, 'fair')
        print_game(game_id, team1_id, team2_id, selected_player_ids[:2], selected_player_ids[2:])
    else:
        print_error("There was an issue at stage: Make sure all selected players are not None before proceeding to create teams and game in select_teams_fair")




def end_game(club_id: int, season_id: int, session_id: int):
# end_game: This function allows the user to end a game within a specific club, season, and session.
# Input: club_id (int) - The ID of the club.
#        season_id (int) - The ID of the season.
#        session_id (int) - The ID of the session.
# Return: Returns nothing.

    session_id = get_session_id(club_id, season_id)

    games = get_ongoing_games(session_id)

    if not games:
        print("No games in progress.")
        return

    while True:
        game_number = input("Enter Game number to end game (Press 0 to exit): ")

        if game_number == '0':
            print("Exiting now.")
            break

        try:
            game_number = int(game_number) - 1  # because list indexing starts at 0
        except ValueError:
            print_error("Invalid input. Please enter a number.")
            continue

        if game_number < 0 or game_number >= len(games):
            print_error("Invalid game number. Please enter a valid game number.")
            continue

        game = games[game_number]
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
                                (team1_score, team2_score, winning_team, game_end_time, game[0]))

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
                    print_error(f"Could not end game: {e}")
                    conn.rollback()
                else:
                    conn.commit()
                    print("Game ended successfully.")
                    break
