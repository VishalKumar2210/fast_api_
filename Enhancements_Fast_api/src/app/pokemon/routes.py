from typing import Annotated, List, Literal, Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from src.app.auth.auth import get_current_user, role_checker
from src.app.auth.auth import router as auth_router
from src.app.auth.models import UserRole
from src.app.database.database import get_db
from src.app.pokemon import models
from src.app.pokemon.schemas import (
    PokemonGetOutputSchema,
    PokemonPatchInputSchema,
    PokemonPostPatchPutOutputSchema,
    PokemonPostPutInputSchema,
)

# FastAPI application initialization
router = APIRouter()

router.include_router(auth_router)
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get(
    "/pokemon/{pokemon_id}",
    response_model=PokemonGetOutputSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(role_checker([UserRole.admin, UserRole.user, UserRole.moderator]))
    ],
)
def get_Pokemon_By_Id(pokemon_id: int, db: Session = Depends(get_db)):
    getSinglePokemon = (
        db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    )

    if not getSinglePokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found."
        )

    return getSinglePokemon


@router.post(
    "/pokemon",
    response_model=PokemonPostPatchPutOutputSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_checker([UserRole.admin]))],
)
def add_Pokemon(pokemon: PokemonPostPutInputSchema, db: Session = Depends(get_db)):
    newPokemon = models.PokemonData(**pokemon.dict())
    db.add(newPokemon)
    db.commit()
    db.refresh(newPokemon)  # This will populate the autoincremented id

    return newPokemon


@router.put(
    "/pokemon/{pokemon_id}",
    response_model=PokemonPostPatchPutOutputSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(role_checker([UserRole.admin]))],
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

    for key, value in pokemon.dict().items():
        setattr(find_pokemon, key, value)

    db.commit()
    db.refresh(find_pokemon)
    return find_pokemon


@router.patch(
    "/pokemon/{pokemon_id}",
    response_model=PokemonPostPatchPutOutputSchema,
    dependencies=[Depends(role_checker([UserRole.admin]))],
)
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
    db.refresh(find_pokemon)
    return find_pokemon


@router.delete(
    "/pokemon/{pokemon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_checker([UserRole.admin]))],
)
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


@router.post("/pokemon/load", dependencies=[Depends(role_checker([UserRole.admin]))])
def fetch_and_store(db: Session = Depends(get_db)):
    response = requests.get("https://coralvanda.github.io/pokemon_data.json")
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to load data."
        )
    data = response.json()

    print(f"Data fetched: {len(data)} entries")

    # Prepare the bulk data mapping
    pokemon_list = []
    for pokemon in data:
        # Map the API data fields to the database model fields
        pokemon_dict = {
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
        # current_id += 1  # Increment the ID for the next Pokémon

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


@router.get(
    "/pokemon/",
    response_model=List[PokemonGetOutputSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(role_checker([UserRole.admin, UserRole.user, UserRole.moderator]))
    ],
)
def get_all_pokemon(
    db: Session = Depends(get_db),
    sort_order: Literal["asc", "desc"] = Query(
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

    # need to add else condition for string

    # Apply sorting
    query = query.order_by(order_by)

    # Pagination: limit and offset
    offset = (page - 1) * limit
    pokemon_list = query.limit(limit).offset(offset).all()

    # Return paginated results
    return pokemon_list
