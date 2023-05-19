from flask import Flask, Blueprint, render_template, request, redirect, jsonify

import psycopg2

def main():
  app = Flask(__name__)

  # Create a database connection.
  db = psycopg2.connect(
    dbname="badminton",
    user="amitsanghvi",
    password="joy4unme",
    host="localhost",
    port="5432",
  )

  # Create a model for each table in the schema.
  player_model = PlayerModel(db)
  club_model = ClubModel(db)
  season_model = SeasonModel(db)
  session_model = SessionModel(db)
  team_model = TeamModel(db)
  game_model = GameModel(db)

  # Create a view for each table in the schema.
  player_view = PlayerView(player_model)
  club_view = ClubView(club_model)
  season_view = SeasonView(season_model)
  session_view = SessionView(session_model)
  team_view = TeamView(team_model)
  game_view = GameView(game_model)

  # Create a controller for each view.
  player_controller = PlayerController(player_view)
  club_controller = ClubController(club_view)
  season_controller = SeasonController(season_view)
  session_controller = SessionController(session_view)
  team_controller = TeamController(team_view)
  game_controller = GameController(game_view)

  # Register the views and controllers with the application.
  app.register_blueprint(player_view.get_blueprint())
  app.register_blueprint(club_view.get_blueprint())
  app.register_blueprint(season_view.get_blueprint())
  app.register_blueprint(session_view.get_blueprint())
  app.register_blueprint(team_view.get_blueprint())
  app.register_blueprint(game_view.get_blueprint())

  # Run the application.
  app.run(debug=True)




from flask import Flask, Blueprint, request, jsonify
import psycopg2

# Model for the "Player" table
class PlayerModel:
    def __init__(self, db):
        self.db = db

    def get_players(self):
        # Retrieve all players from the database
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM players")
            return cursor.fetchall()

    def delete_player(self, player_id):
        # Delete a player and their associated records from the database
        with self.db.cursor() as cursor:
            cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
            cursor.execute("DELETE FROM child_table WHERE player_id = %s", (player_id,))
        self.db.commit()


# View for the "Player" table
class PlayerView:
    def __init__(self, player_model):
        self.player_model = player_model

    def get_players(self):
        players = self.player_model.get_players()
        return players

    def delete_player(self, player_id):
        self.player_model.delete_player(player_id)



# Controller for the "Player" table
class PlayerController:
    def __init__(self, player_view):
        self.player_view = player_view

    def register_routes(self, app):
        # Register the routes with the Flask application
        app.add_url_rule("/", "index", self.index)
        app.add_url_rule("/players", "players", self.players)
        app.add_url_rule("/players/delete/<int:player_id>", "delete_player", self.delete_player)

    def index(self):
        # Render the index.html template
        return render_template("index.html")

    def players(self):
        players = self.player_view.get_players()
        # Render the players.html template with the retrieved players
        return render_template("players.html", players=players)

    def delete_player(self, player_id):
        self.player_view.delete_player(player_id)
        # Redirect to the players route after deleting a player
        return redirect("/players")

def main():
    app = Flask(__name__)

    # Create a database connection.
    db = psycopg2.connect(
        dbname="badminton",
        user="amitsanghvi",
        password="joy4unme",
        host="localhost",
        port="5432",
    )

    # Create a model for the "Player" table.
    player_model = PlayerModel(db)

    # Create a view for the "Player" table.
    player_view = PlayerView(player_model)

    # Create a controller for the "Player" table.
    player_controller = PlayerController(player_view)

    # Register the routes with the application.
    player_controller.register_routes(app)

    # Run the application.
    app.run(debug=True)

if __name__ == "__main__":
    main()