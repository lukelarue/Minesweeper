CREATE TABLE user_profiles (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  hashed_password CHAR(60) NOT NULL, -- bcrypted passwords will be 60 characters
  created_ip VARCHAR(45) NOT NULL, -- Max length of IPv6
  last_login_ip VARCHAR(45) DEFAULT NULL,
  account_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP DEFAULT NULL,
  email VARCHAR(255) UNIQUE NOT NULL
);

CREATE OR REPLACE FUNCTION set_last_login_and_ip() RETURNS TRIGGER AS $$
BEGIN
  NEW.last_login := NEW.account_created;
  NEW.last_login_ip := NEW.created_ip;
  RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER set_last_login_and_ip_trigger
BEFORE INSERT ON user_profiles
FOR EACH ROW EXECUTE FUNCTION set_last_login_and_ip();

CREATE TABLE games (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES user_profiles(id),
  mines integer[] NOT NULL,
  board_size INTEGER NOT NULL,
  number_of_moves INTEGER NOT NULL,
  tiles_revealed INTEGER NOT NULL,
  game_status CHAR(1) NOT NULL CHECK (game_status IN ('W', 'L', 'U')), -- 'W' for win, 'L' for loss, 'U' for unfinished
  game_start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  game_end_time TIMESTAMP
);

CREATE TABLE game_history (
  id SERIAL PRIMARY KEY,
  game_id INTEGER REFERENCES games(id),
  move_number INTEGER NOT NULL,
  move_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  tile_position INTEGER NOT NULL
);
