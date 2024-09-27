from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
import requests
from database import SessionLocal, engine
from fastapi import Query
from typing import Optional, List

import models
from schemas import (
    PokemonPostPutInputSchema,
    PokemonPatchInputSchema,
    PokemonGetOutputSchema,
    PokemonPostPatchPutOutputSchema,
)
from typing import List

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get(
    "/pokemon_all",
    response_model=List[PokemonGetOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_all_pokemon(db: Session = Depends(get_db)):
    getAllPokemon = db.query(models.PokemonData).all()
    return getAllPokemon


@app.get(
    "/pokemon/{pokemon_id}",
    response_model=PokemonGetOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_Pokemon_By_Id(pokemon_id: int, db: Session = Depends(get_db)):
    getSinglePokemon = (
        db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    )
    if getSinglePokemon:
        return getSinglePokemon
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found.."
        )


@app.post(
    "/pokemon",
    response_model=PokemonPostPatchPutOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def add_Pokemon(pokemon: PokemonPostPutInputSchema, db: Session = Depends(get_db)):
    max_id_obj = (
        db.query(models.PokemonData.id).order_by(models.PokemonData.id.desc()).first()
    )
    new_id = max_id_obj[0] + 1 if max_id_obj else 1  # If no records, start with id=1

    newPokemon = models.PokemonData(
        id=new_id,
        name=pokemon.name,
        type_1=pokemon.type_1,
        type_2=pokemon.type_2,
        total=pokemon.total,
        hp=pokemon.hp,
        attack=pokemon.attack,
        defense=pokemon.defense,
        sp_atk=pokemon.sp_atk,
        sp_def=pokemon.sp_def,
        speed=pokemon.speed,
        generation=pokemon.generation,
        legendary=pokemon.legendary,
    )
    db.add(newPokemon)
    db.commit()
    db.refresh(newPokemon)
    return newPokemon


@app.put(
    "/pokemon/{pokemon_id}",
    response_model=PokemonPostPatchPutOutputSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_Pokemon(
    pokemon_id: int, pokemon: PokemonPostPutInputSchema, db: Session = Depends(get_db)
):
    find_pokemon = (
        db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    )
    if not find_pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pokemon with this id does not exist.",
        )

    find_pokemon.name = pokemon.name
    find_pokemon.type_1 = pokemon.type_1
    find_pokemon.type_2 = pokemon.type_2
    find_pokemon.total = pokemon.total
    find_pokemon.hp = pokemon.hp
    find_pokemon.attack = pokemon.attack
    find_pokemon.defense = pokemon.defense
    find_pokemon.sp_atk = pokemon.sp_atk
    find_pokemon.sp_def = pokemon.sp_def
    find_pokemon.speed = pokemon.speed
    find_pokemon.generation = pokemon.generation
    find_pokemon.legendary = pokemon.legendary

    db.commit()
    return find_pokemon


@app.patch("/pokemon/{pokemon_id}", response_model=PokemonPostPatchPutOutputSchema)
def update_Pokemon_Patch(
    pokemon_id: int, pokemon: PokemonPatchInputSchema, db: Session = Depends(get_db)
):
    find_pokemon = (
        db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    )
    if not find_pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokemon with id {pokemon_id} doesn't exist...",
        )

    for key, value in pokemon.dict(exclude_unset=True).items():
        setattr(find_pokemon, key, value)

    db.commit()
    return find_pokemon


@app.delete("/pokemon/{pokemon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_Pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    find_pokemon = (
        db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    )

    if not find_pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found"
        )

    db.delete(find_pokemon)
    db.commit()
    return None


@app.post("/pokemon/")
def fetch_and_store(db: Session = Depends(get_db)):
    response = requests.get("https://coralvanda.github.io/pokemon_data.json")
    data = response.json()

    print(f"Data fetched: {len(data)} entries")

    # Fetch the current max ID in the database
    max_id = db.query(func.max(models.PokemonData.id)).scalar() or 0
    current_id = max_id + 1

    # Prepare the bulk data mapping
    pokemon_list = []
    for pokemon in data:
        # Map the API data fields to the database model fields
        pokemon_dict = {
            "id": current_id,
            "name": pokemon["Name"],
            "type_1": pokemon["Type 1"],
            "type_2": pokemon.get("Type 2", None),  # Handle optional type_2 field
            "total": pokemon["Total"],
            "hp": pokemon["HP"],
            "attack": pokemon["Attack"],
            "defense": pokemon["Defense"],
            "sp_atk": pokemon["Sp. Atk"],
            "sp_def": pokemon["Sp. Def"],
            "speed": pokemon["Speed"],
            "generation": pokemon["Generation"],
            "legendary": pokemon["Legendary"],
        }
        pokemon_list.append(pokemon_dict)
        current_id += 1  # Increment the ID for the next Pokémon

    # Perform bulk insert using bulk_insert_mappings
    try:
        db.bulk_insert_mappings(models.PokemonData, pokemon_list)
        db.commit()
    except Exception as e:
        db.rollback()  # Rollback transaction in case of error
        return {"error": str(e)}

    return {
        "message": "Data successfully stored in the database",
        "inserted": len(pokemon_list),
    }


@app.get(
    "/pokemon/",
    response_model=List[PokemonGetOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_all_pokemon(
    db: Session = Depends(get_db),
    sort_order: Optional[str] = Query(
        "asc", description="Order by Ascending or Descending (asc/desc)"
    ),
    search_column: Optional[str] = Query("name", description="Column to search in"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    limit: int = Query(10, description="Limit the number of results per page"),
    page: int = Query(1, description="Page number for pagination"),
):
    # Handle sorting
    order_by = (
        asc(models.PokemonData.id)
        if sort_order.lower() == "asc"
        else desc(models.PokemonData.id)
    )

    # Create the base query
    query = db.query(models.PokemonData)

    # Handle search functionality (search in the user-specified column or default to "name")
    if keyword:
        column_to_search = getattr(models.PokemonData, search_column, None)
        if column_to_search is None:
            raise HTTPException(
                status_code=400, detail=f"Invalid column name: {search_column}"
            )
        query = query.filter(column_to_search.ilike(f"%{keyword}%"))

    # Apply sorting
    query = query.order_by(order_by)

    # Pagination: limit and offset
    offset = (page - 1) * limit
    pokemon_list = query.limit(limit).offset(offset).all()

    # Return paginated results
    return pokemon_list
