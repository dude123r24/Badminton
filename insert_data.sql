

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Amit Sanghvi', 'amit2u@hotmail.com', '00447788654654', 'password1', '2022-01-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Sunil Tiwari', 'suntiltiwari@hotmail.com', '00447788654654', 'password2', '2022-03-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Sudheer Dasari', 'Sudheer@hotmail.com', '00447788654654', 'password3', '2022-04-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Prashant Mehta', 'Prashant@hotmail.com', '00447788654654', 'password4', '2022-05-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Anil Bakrania', 'Anil@hotmail.com', '00447788654654', 'password5', '2022-06-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Pratik Bakrania', 'Pratik@hotmail.com', '00447788654654', 'password6', '2022-07-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Pranay', 'Pranay@hotmail.com', '00447788654654', 'password7', '2022-08-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Bipin Pindoria', 'Bipin@hotmail.com', '00447788654654', 'password8', '2022-09-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Amit Shah', 'Amit@hotmail.com', '00447788654654', 'password9', '2022-10-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Noah Sheldon', 'Noah@hotmail.com', '00447788654654', 'password10', '2022-11-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Yee', 'yee@hotmail.com', '00447788654654', 'password11', '2022-12-01') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Neal Sarangdhar', 'Neal@hotmail.com', '00447788654654', 'password12', '2021-02-02') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Sunil Mistry', 'sunilm@hotmail.com', '00447788654654', 'password13', '2021-12-02') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Amit Mittal', 'amitm@hotmail.com', '00447788654654', 'password14', '2022-10-02') ;

INSERT INTO players (name, email, phone, password, date_joined) 
VALUES ('Aaquil', 'Aaquil@hotmail.com', '00447788654654', 'password15', '2023-11-02') ;


INSERT INTO clubs (name, date_formed, no_of_courts, created_by, addr_line1, locality, city, country, postcode)
VALUES
   ('Swaggers', '2022-10-01', 2, 1, '123 Main St', 'Downtown', 'Watford', 'UK', 'SW1A 1AA'),
   ('X-Men(Tuesday)', '2022-04-01', 10, 4, '111 Cherry St', 'Downtown', 'London', 'UK', 'SW1A 1AA'),
   ('X-Men(Thursday)', '2022-05-01', 12, 11, '222 Pine St', 'Uptown', 'London', 'UK', 'WC1A 1AA');


INSERT INTO club_options (club_id,option_name,option_value) VALUES
     (1,'max_players_per_court',4),
     (1,'session_duration','2'),
     (1,'num_courts','2'),
     (1,'algorithm','random');


INSERT INTO players_clubs (club_id, player_id, role, grade, ranking, approved, archived)
VALUES
(1, 1, 'owner', 'A', 1, true, false),
(1, 2, 'member', 'B', 2, true, false),
(1, 3, 'member', 'B', 2, true, false),
(1, 4, 'member', 'B', 2, true, false),
(1, 5, 'member', 'B', 2, true, false),
(1, 6, 'member', 'B', 2, true, false),
(1, 7, 'member', 'B', 2, true, false),
(1, 8, 'member', 'B', 2, true, false),
(1, 9, 'member', 'B', 2, true, false),
(1, 10, 'member', 'B', 2, true, false),
(1, 11, 'member', 'B', 2, true, false),
(1, 12, 'member', 'B', 2, true, false),
(1, 13, 'member', 'B', 2, true, false),
(1, 14, 'member', 'B', 2, true, false),
(1, 15, 'member', 'B', 2, true, false),
(2, 1, 'member', 'C', 3, true, false),
(2, 9, 'member', 'A', 1, true, false);


INSERT INTO seasons (club_id, date_from, date_to)
VALUES
(1, '2022-01-01', '2022-06-30'),
(1, '2023-04-01', '2023-06-30'),
(1, '2023-01-01', '2023-03-31');