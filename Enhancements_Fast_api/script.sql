-- pokemon_database_creation.sql
CREATE DATABASE pokemon_data;

-- pokemon_table_creation.sql
CREATE TABLE pokemon_data_test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    type_1 VARCHAR(40) NOT NULL,
    type_2 VARCHAR(40),
    total INTEGER NOT NULL,
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    sp_atk INTEGER NOT NULL,
    sp_def INTEGER NOT NULL,
    speed INTEGER NOT NULL,
    generation INTEGER NOT NULL,
    legendary BOOLEAN NOT NULL
);

-- pokemon_table_insert.sql
INSERT INTO pokemon_roster (name, type_1, type_2, total, hp, attack, defense, sp_atk, sp_def, speed, generation, legendary)
VALUES
    ('Charmander', 'Fire', NULL, 309, 39, 52, 43, 60, 50, 65, 1, false),
    ('Squirtle', 'Water', NULL, 314, 44, 48, 65, 50, 64, 43, 1, false),
    ('Articuno', 'Ice', 'Flying', 580, 90, 85, 100, 95, 125, 85, 1, true);

