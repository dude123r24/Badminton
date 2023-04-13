CREATE OR REPLACE FUNCTION public.get_games_for_player(p_player_id INTEGER)
RETURNS TABLE (
    game_id INTEGER,
    club_id INTEGER,
    season_id INTEGER,
    session_id INTEGER,
    team_1 INTEGER,
    team_2 INTEGER,
    team_1_score INTEGER,
    team_2_score INTEGER,
    winning_team INTEGER,
    game_start_time TIMESTAMP,
    game_end_time TIMESTAMP,
    player_team TEXT,
    player_team_id INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        gv.game_id,
        gv.club_id,
        gv.season_id,
        gv.session_id,
        gv.team_1,
        gv.team_2,
        gv.team_1_score,
        gv.team_2_score,
        gv.winning_team,
        gv.game_start_time,
        gv.game_end_time,
        CASE
            WHEN p_player_id = ANY(gv.team_1_player_ids) THEN 'team_1'
            ELSE 'team_2'
        END AS player_team,
        CASE
            WHEN p_player_id = ANY(gv.team_1_player_ids) THEN gv.team_1
            ELSE gv.team_2
        END AS player_team_id
    FROM
        public.games_view gv
    WHERE
        p_player_id = ANY(gv.team_1_player_ids) OR p_player_id = ANY(gv.team_2_player_ids);
END;
$$ LANGUAGE plpgsql;

-- Sample usage : SELECT * FROM public.get_games_for_player(1);