CREATE TABLE IF NOT EXISTS players (
   id serial PRIMARY KEY,
   name varchar(75) NOT NULL,
   email varchar(75) NOT NULL,
   phone varchar(20) NOT NULL,
   password varchar(128) NOT NULL,
   date_joined timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clubs (
   id serial PRIMARY KEY,
   name varchar(255) NOT NULL,
   date_formed timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
   no_of_courts integer NOT NULL DEFAULT 0,
   created_by integer NOT NULL REFERENCES players(id),
   addr_line1 varchar(255) NOT NULL,
   locality varchar(255) NOT NULL,
   city varchar(255) NOT NULL,
   country varchar(255) NOT NULL,
   postcode varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS players_clubs (
   id serial PRIMARY KEY,
   club_id integer NOT NULL REFERENCES clubs(id),
   player_id integer NOT NULL REFERENCES players(id),
   role varchar(25) NOT NULL,
   grade varchar(3) NOT NULL,
   ranking integer NOT NULL,
   approved boolean NOT NULL DEFAULT false,
   archived boolean NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS seasons (
   id serial PRIMARY KEY,
   club_id integer NOT NULL REFERENCES clubs(id),
   date_from date NOT NULL,
   date_to date NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
   id serial PRIMARY KEY,
   season_id integer NOT NULL REFERENCES seasons(id),
   club_id integer NOT NULL REFERENCES clubs(id),
   session_date date NOT NULL,
   no_of_courts integer NOT NULL,
   no_of_players_per_court integer NOT NULL,
   players_played text NOT NULL DEFAULT 0
);
ALTER TABLE sessions ADD CONSTRAINT sessions_un UNIQUE (session_date,club_id,season_id);


CREATE TABLE sessions_players (
    id serial NOT NULL,
    session_id integer NOT NULL,
    player_id integer NOT NULL,
    active varchar NOT NULL DEFAULT 'Y'::character varying,
    played integer NOT NULL DEFAULT 0,
    won integer NOT NULL DEFAULT 0,
    draw integer NOT NULL DEFAULT 0,
--    win_percentage numeric(5, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT sessions_players_un UNIQUE (session_id, player_id),
    CONSTRAINT sessions_players_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(id),
    CONSTRAINT sessions_players_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id)
);
COMMENT ON COLUMN sessions_players.active IS 'When a player is selected to play in the session this column is Y. When they are done for the day, and end their session, it becomes N. If the session is ended without players ending their session, the values will becomes N automatically next time a new session is created. It does not have to be set to N, as the next session it will only look at that sessions active players';


CREATE TABLE IF NOT EXISTS teams (
   id serial PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS teams_players (
   team_id integer NOT NULL REFERENCES teams(id),
   player_id integer NOT NULL REFERENCES players(id),
   PRIMARY KEY (team_id, player_id)
);

CREATE TABLE IF NOT EXISTS games (
   id serial PRIMARY KEY,
   session_id integer NOT NULL REFERENCES sessions(id),
   team1_id integer NOT NULL REFERENCES teams(id),
   team2_id integer NOT NULL REFERENCES teams(id),
   team1_score integer NOT NULL,
   team2_score integer NOT NULL,
   winner_team_id integer REFERENCES teams(id),
   game_start_time timestamp NOT NULL,
   game_end_time timestamp
);

CREATE TABLE  IF NOT EXISTS club_options (
  id SERIAL,
  club_id INTEGER NOT NULL REFERENCES clubs(id),
  option_name VARCHAR(255) NOT NULL,
  option_value VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
ALTER TABLE club_options ADD CONSTRAINT club_options_pk PRIMARY KEY (club_id, option_name);
