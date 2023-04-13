DROP TABLE IF EXISTS clubs cascade ;
DROP TABLE IF EXISTS players cascade ;
DROP TABLE IF EXISTS players_clubs cascade ;
DROP TABLE IF EXISTS seasons cascade ;
DROP TABLE IF EXISTS sessions cascade ;
DROP TABLE IF EXISTS sessions_players cascade ;
DROP TABLE IF EXISTS teams cascade ;
DROP TABLE IF EXISTS teams_players cascade ;
DROP TABLE IF EXISTS games cascade ;
DROP TABLE IF EXISTS club_options cascade ;

DROP VIEW IF EXISTS games_detail ;
DROP VIEW IF EXISTS season_player_stats ;
DROP VIEW IF EXISTS club_player_stats ;
DROP VIEW IF EXISTS player_stats_by_session ;
DROP VIEW IF EXISTS player_combinations_by_session ;


drop function public.get_games_for_player;