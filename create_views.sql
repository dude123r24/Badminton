CREATE OR REPLACE VIEW games_view
AS SELECT g.id AS game_id,
    s.club_id,
    s.season_id,
    g.session_id,
    g.team1_id AS team_1,
    g.team2_id AS team_2,
    g.team1_score AS team_1_score,
    g.team2_score AS team_2_score,
    g.winner_team_id AS winning_team,
    array_agg(DISTINCT tp1.player_id) AS team_1_player_ids,
    array_agg(DISTINCT tp2.player_id) AS team_2_player_ids,
    array_agg(DISTINCT p1.name) AS team_1_player_names,
    array_agg(DISTINCT p2.name) AS team_2_player_names,
    game_start_time,
    game_end_time
FROM games g
    JOIN sessions s ON g.session_id = s.id
    JOIN teams t1 ON g.team1_id = t1.id
    JOIN teams t2 ON g.team2_id = t2.id
    JOIN teams_players tp1 ON t1.id = tp1.team_id
    JOIN teams_players tp2 ON t2.id = tp2.team_id
    JOIN players p1 ON tp1.player_id = p1.id
    JOIN players p2 ON tp2.player_id = p2.id
GROUP BY g.id, g.session_id, s.season_id, s.club_id, g.team1_id, g.team2_id, g.team1_score, g.team2_score, g.winner_team_id;


CREATE OR REPLACE VIEW player_stats_by_session
AS 
SELECT 
    s.club_id,
    s.season_id,
    s.id AS session_id,
    s.session_date,
    sp.player_id,
    p.name AS player_name,
    sp.played,
    sp.won,
    sp.draw,
    ROUND(100.0 * sp.won / NULLIF(sp.played , 0), 2) AS win_percentage,
    round(AVG(ABS(g.team1_score - g.team2_score)) FILTER (WHERE g.winner_team_id = tp.team_id),2) AS avg_victory_margin,
    MIN(ge.minutes_since_last_game) AS minutes_since_last_game,
    DENSE_RANK() OVER (PARTITION BY s.id ORDER BY ROUND(100.0 * COUNT(*) FILTER (WHERE g.winner_team_id = tp.team_id) / NULLIF(COUNT(g.id), 0), 2) DESC, AVG(ABS(g.team1_score - g.team2_score)) FILTER (WHERE g.winner_team_id = tp.team_id) DESC) AS session_rank
FROM 
    sessions_players sp
JOIN 
    players p ON sp.player_id = p.id
JOIN 
    sessions s ON sp.session_id = s.id
JOIN 
    teams_players tp ON sp.player_id = tp.player_id
JOIN 
    games g ON g.session_id = s.id AND (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
JOIN
    ( SELECT 
  g.id AS game_id, 
  tp.player_id, 
  round(ABS(EXTRACT(EPOCH FROM (g.game_end_time - now())) / 60),0) AS minutes_since_last_game
FROM teams_players tp 
JOIN games g ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id) ) ge ON ge.game_id = g.id AND ge.player_id = sp.player_id
GROUP BY 
    s.club_id, s.season_id, s.id, s.session_date, sp.player_id, p.name, sp.played, sp.won, sp.draw ;



CREATE OR REPLACE VIEW player_stats_by_season
AS 
SELECT 
    s.club_id,
    s.season_id,
    sp.player_id,
    p.name AS player_name,
    COUNT(g.id) AS games_played,
    COUNT(*) FILTER (WHERE g.winner_team_id = tp.team_id) AS games_won,
    COUNT(*) FILTER (WHERE g.winner_team_id IS NULL) AS games_draw,
    ROUND(100.0 * COUNT(*) FILTER (WHERE g.winner_team_id = tp.team_id) / NULLIF(COUNT(g.id), 0), 2) AS win_percentage,
    ROUND(AVG(ABS(g.team1_score - g.team2_score)) FILTER (WHERE g.winner_team_id = tp.team_id), 2) AS avg_victory_margin,
    DENSE_RANK() OVER (PARTITION BY s.season_id ORDER BY ROUND(100.0 * COUNT(*) FILTER (WHERE g.winner_team_id = tp.team_id) / NULLIF(COUNT(g.id), 0), 2) DESC, AVG(ABS(g.team1_score - g.team2_score)) FILTER (WHERE g.winner_team_id = tp.team_id) DESC) AS season_rank,
    se.date_from,
    se.date_to
FROM 
    sessions_players sp
JOIN 
    players p ON sp.player_id = p.id
JOIN 
    sessions s ON sp.session_id = s.id
JOIN 
    seasons se ON s.season_id = se.id
JOIN 
    teams_players tp ON sp.player_id = tp.player_id
JOIN 
    games g ON g.session_id = s.id AND (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
GROUP BY 
    s.season_id, s.club_id, sp.player_id, p.name, se.date_from, se.date_to;


CREATE OR REPLACE VIEW player_stats_by_club
AS 
SELECT 
    c.id AS club_id,
    c.name AS club_name,
    c.city AS club_city,
    c.country AS club_country,
    c.postcode AS club_postcode,
    sp.player_id,
    p.name AS player_name,
    COUNT(g.id) AS games_played,
    COUNT(*) FILTER (WHERE g.winner_team_id = tp.team_id) AS games_won,
    COUNT(*) FILTER (WHERE g.winner_team_id IS NULL) AS games_draw,
    ROUND(100.0 * COUNT(*) FILTER (WHERE g.winner_team_id = tp.team_id) / NULLIF(COUNT(g.id), 0), 2) AS win_percentage,
    ROUND(AVG(ABS(g.team1_score - g.team2_score)) FILTER (WHERE g.winner_team_id = tp.team_id), 2) AS avg_victory_margin,
    DENSE_RANK() OVER (PARTITION BY c.id ORDER BY ROUND(100.0 * COUNT(*) FILTER (WHERE g.winner_team_id = tp.team_id) / NULLIF(COUNT(g.id), 0), 2) DESC, AVG(ABS(g.team1_score - g.team2_score)) FILTER (WHERE g.winner_team_id = tp.team_id) DESC) AS club_rank
FROM 
    sessions_players sp
JOIN 
    players p ON sp.player_id = p.id
JOIN 
    sessions s ON sp.session_id = s.id
JOIN 
    clubs c ON s.club_id = c.id
JOIN 
    teams_players tp ON sp.player_id = tp.player_id
JOIN 
    games g ON g.session_id = s.id AND (g.team1_id = tp.team_id OR g.team2_id = tp.team_id)
GROUP BY 
    c.id, sp.player_id, p.name;




CREATE OR REPLACE VIEW player_combinations_by_session AS
WITH player_games AS (
         SELECT ss.id AS session_id,
            ss.season_id,
            c.id AS club_id,
            sp.player_id,
            p.name AS player_name,
            tp.team_id,
            g.id AS game_id,
            g.winner_team_id,
            g.team1_score,
            g.team2_score,
                CASE
                    WHEN g.winner_team_id IS NULL THEN 'draw'::text
                    WHEN g.winner_team_id = tp.team_id THEN 'won'::text
                    ELSE 'lost'::text
                END AS game_result
           FROM sessions ss
             JOIN seasons s ON ss.season_id = s.id
             JOIN clubs c ON s.club_id = c.id
             JOIN sessions_players sp ON ss.id = sp.session_id
             JOIN players p ON sp.player_id = p.id
             JOIN teams_players tp ON sp.player_id = tp.player_id
             JOIN games g ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id) AND ss.id = g.session_id
        ), teammate_info AS (
         SELECT pg1.session_id,
            pg1.season_id,
            pg1.club_id,
            LEAST(pg1.player_id, pg2.player_id) AS player_id_1,
            GREATEST(pg1.player_id, pg2.player_id) AS player_id_2,
            pg1.game_id,
            pg1.game_result,
            pg1.team1_score,
            pg1.team2_score
           FROM player_games pg1
             JOIN player_games pg2 ON pg1.game_id = pg2.game_id AND pg1.team_id = pg2.team_id AND pg1.player_id <> pg2.player_id
        )
 SELECT 
    ti.club_id,
    ti.season_id,
    ti.session_id,
    p1.id AS player_id_1,
    p1.name AS player_name_1,
    p2.id AS player_id_2,
    p2.name AS player_name_2,
    count(*) AS games_played,
    count(*) FILTER (WHERE ti.game_result = 'won'::text) AS games_won,
    count(*) FILTER (WHERE ti.game_result = 'lost'::text) AS games_lost,
    count(*) FILTER (WHERE ti.game_result = 'draw'::text) AS games_draw,
    round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2) AS win_percentage,
    avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) AS avg_margin_victory,
    dense_rank() OVER (PARTITION BY ti.session_id, ti.club_id ORDER BY (round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2)) DESC, avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) DESC, (count(*)) DESC) AS session_rank
   FROM teammate_info ti
     JOIN players p1 ON ti.player_id_1 = p1.id
     JOIN players p2 ON ti.player_id_2 = p2.id
  GROUP BY ti.session_id, ti.season_id, ti.club_id, p1.id, p1.name, p2.id, p2.name
  ORDER BY ti.club_id, ti.season_id, ti.session_id;


CREATE OR REPLACE VIEW player_combinations_by_season AS
WITH player_games AS (
         SELECT 
            c.id AS club_id,
            ss.season_id,
            sp.player_id,
            p.name AS player_name,
            tp.team_id,
            g.id AS game_id,
            g.winner_team_id,
            g.team1_score,
            g.team2_score,
                CASE
                    WHEN g.winner_team_id IS NULL THEN 'draw'::text
                    WHEN g.winner_team_id = tp.team_id THEN 'won'::text
                    ELSE 'lost'::text
                END AS game_result
           FROM seasons s
             JOIN clubs c ON s.club_id = c.id
             JOIN sessions ss ON s.id = ss.season_id
             JOIN sessions_players sp ON ss.id = sp.session_id
             JOIN players p ON sp.player_id = p.id
             JOIN teams_players tp ON sp.player_id = tp.player_id
             JOIN games g ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id) AND ss.id = g.session_id
        ), teammate_info AS (
         SELECT pg1.season_id,
            pg1.club_id,
            LEAST(pg1.player_id, pg2.player_id) AS player_id_1,
            GREATEST(pg1.player_id, pg2.player_id) AS player_id_2,
            pg1.game_id,
            pg1.game_result,
            pg1.team1_score,
            pg1.team2_score
           FROM player_games pg1
             JOIN player_games pg2 ON pg1.game_id = pg2.game_id AND pg1.team_id = pg2.team_id AND pg1.player_id <> pg2.player_id
        )
 SELECT ti.season_id,
    ti.club_id,
    p1.id AS player_id_1,
    p1.name AS player_name_1,
    p2.id AS player_id_2,
    p2.name AS player_name_2,
    count(*) AS games_played,
    count(*) FILTER (WHERE ti.game_result = 'won'::text) AS games_won,
    count(*) FILTER (WHERE ti.game_result = 'lost'::text) AS games_lost,
    count(*) FILTER (WHERE ti.game_result = 'draw'::text) AS games_draw,
    round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2) AS win_percentage,
    avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) AS avg_margin_victory,
    dense_rank() OVER (PARTITION BY ti.season_id, ti.club_id ORDER BY (round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2)) DESC, avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) DESC, (count(*)) DESC) AS season_rank
   FROM teammate_info ti
     JOIN players p1 ON ti.player_id_1 = p1.id
     JOIN players p2 ON ti.player_id_2 = p2.id
  GROUP BY ti.season_id, ti.club_id, p1.id, p1.name, p2.id, p2.name
  ORDER BY ti.season_id, round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2) desc, avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) DESC, p1.id, p2.id;


CREATE OR REPLACE VIEW player_combinations_by_club AS
WITH player_games AS (
         SELECT c.id AS club_id,
            sp.player_id,
            p.name AS player_name,
            tp.team_id,
            g.id AS game_id,
            g.winner_team_id,
            g.team1_score,
            g.team2_score,
                CASE
                    WHEN g.winner_team_id IS NULL THEN 'draw'::text
                    WHEN g.winner_team_id = tp.team_id THEN 'won'::text
                    ELSE 'lost'::text
                END AS game_result
           FROM clubs c
             JOIN sessions s ON c.id = s.club_id
             JOIN sessions_players sp ON s.id = sp.session_id
             JOIN players p ON sp.player_id = p.id
             JOIN teams_players tp ON sp.player_id = tp.player_id
             JOIN games g ON (g.team1_id = tp.team_id OR g.team2_id = tp.team_id) AND s.id = g.session_id
        ), teammate_info AS (
         SELECT pg1.club_id,
            LEAST(pg1.player_id, pg2.player_id) AS player_id_1,
            GREATEST(pg1.player_id, pg2.player_id) AS player_id_2,
            pg1.game_id,
            pg1.game_result,
            pg1.team1_score,
            pg1.team2_score
           FROM player_games pg1
             JOIN player_games pg2 ON pg1.game_id = pg2.game_id AND pg1.team_id = pg2.team_id AND pg1.player_id <> pg2.player_id
        )
 SELECT ti.club_id,
    p1.id AS player_id_1,
    p1.name AS player_name_1,
    p2.id AS player_id_2,
    p2.name AS player_name_2,
    count(*) AS games_played,
    count(*) FILTER (WHERE ti.game_result = 'won'::text) AS games_won,
    count(*) FILTER (WHERE ti.game_result = 'lost'::text) AS games_lost,
    count(*) FILTER (WHERE ti.game_result = 'draw'::text) AS games_draw,
    round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2) AS win_percentage,
    avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) AS avg_margin_victory,
    dense_rank() OVER (PARTITION BY ti.club_id ORDER BY (round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2)) DESC, avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) DESC, (count(*)) DESC) AS club_rank
   FROM teammate_info ti
     JOIN players p1 ON ti.player_id_1 = p1.id
     JOIN players p2 ON ti.player_id_2 = p2.id
  GROUP BY ti.club_id, p1.id, p1.name, p2.id, p2.name
  ORDER BY ti.club_id, round((100 * count(*) FILTER (WHERE ti.game_result = 'won'::text) / count(*))::numeric, 2) desc, avg(CASE WHEN ti.game_result = 'won' THEN abs(ti.team1_score - ti.team2_score) ELSE NULL END) DESC
