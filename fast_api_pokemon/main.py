from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List, Optional

app = FastAPI(
    title="Welcome to my FastAPI application",
    description="API for managing Pokémon data",
    version="1.0.0",
)


def get_db_connection():
    conn = psycopg2.connect(
        dbname="pokemon_data",
        user="vishal.chaurasiya",
        password="Password",
        host="localhost",
        port="5432"
    )
    return conn


class Pokemon(BaseModel):
    number: int
    name: str
    type1: str
    type2: Optional[str] = None
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool


# Create (POST)
@app.post("/pokemon/", response_model=Pokemon)
def create_pokemon_data(pokemon: Pokemon):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pokemon (number, name, type1, type2, total, hp, attack, defense, sp_atk, sp_def, speed, generation, legendary)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING number;
    """, (
        pokemon.number,
        pokemon.name,
        pokemon.type1,
        pokemon.type2,
        pokemon.total,
        pokemon.hp,
        pokemon.attack,
        pokemon.defense,
        pokemon.sp_atk,
        pokemon.sp_def,
        pokemon.speed,
        pokemon.generation,
        pokemon.legendary
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return pokemon


# Read (GET)
@app.get("/pokemon/{number}", response_model=Pokemon)
def read_pokemon_data(number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pokemon WHERE number = %s", (number,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return Pokemon(
        number=row[1],
        name=row[2],
        type1=row[3],
        type2=row[4],
        total=row[5],
        hp=row[6],
        attack=row[7],
        defense=row[8],
        sp_atk=row[9],
        sp_def=row[10],
        speed=row[11],
        generation=row[12],
        legendary=row[13]
    )


# Update (PUT)
@app.put("/pokemon/{number}", response_model=Pokemon)
def update_pokemon_data(number: int, updated_pokemon: Pokemon):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE pokemon
    SET name = %s, type1 = %s, type2 = %s, total = %s, hp = %s, attack = %s, defense = %s, sp_atk = %s, sp_def = %s, speed = %s, generation = %s, legendary = %s
    WHERE number = %s
    """, (
        updated_pokemon.name,
        updated_pokemon.type1,
        updated_pokemon.type2,
        updated_pokemon.total,
        updated_pokemon.hp,
        updated_pokemon.attack,
        updated_pokemon.defense,
        updated_pokemon.sp_atk,
        updated_pokemon.sp_def,
        updated_pokemon.speed,
        updated_pokemon.generation,
        updated_pokemon.legendary,
        number
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return updated_pokemon


# Delete (DELETE)
@app.delete("/pokemon/{number}")
def delete_pokemon_data(number: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pokemon WHERE number = %s", (number,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Pokémon deleted successfully"}


# List all Pokémon (GET)
@app.get("/pokemon/", response_model=List[Pokemon])
def list_of_all_pokemon_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pokemon")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        Pokemon(
            number=row[1],
            name=row[2],
            type1=row[3],
            type2=row[4],
            total=row[5],
            hp=row[6],
            attack=row[7],
            defense=row[8],
            sp_atk=row[9],
            sp_def=row[10],
            speed=row[11],
            generation=row[12],
            legendary=row[13]
        ) for row in rows
    ]
