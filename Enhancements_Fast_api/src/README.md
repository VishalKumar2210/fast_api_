
# Pokémon API

A FastAPI-based API designed to manage Pokémon data, including full CRUD operations, search, sorting, and bulk data insertion from an external source.
This project also includes user authentication and authorization as well as comprehensive test cases.

## Features

- **CRUD Operations**: Create, Read, Update, and Delete Pokémon records.
- **Search, Sort, and Pagination**: Easily find Pokémon based on specific criteria and paginate results.
- **Bulk Data Insertion**: Fetch Pokémon data from an external API and store it in the database.
- **User Authentication & Authorization**: Secure access to endpoints with JWT or OAuth.
- **Comprehensive Testing**: Includes pass and fail test cases for each endpoint.

## Requirements

- Python 3.11
- PostgreSQL

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/VishalKumar2210/fast_api_.git
   cd fast_api_
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   - Ensure PostgreSQL is running and create a database for the project.
   - Configure the database URL in `database.py`.

4. **Run the application**:

   ```bash
   uvicorn main:app --reload
   ```

## Endpoints

### Pokémon Data Operations

- **GET** `/pokemon/{pokemon_id}`: Fetch details of a Pokémon by its ID.
- **POST** `/add_Pokemon`: Add a new Pokémon record.
- **PUT** `/update_Pokemon/{pokemon_id}`: Update an existing Pokémon record by ID.
- **PATCH** `/update_Pokemon_Patch/{pokemon_id}`: Partially update a Pokémon record by ID.
- **DELETE** `/delete_Pokemon/{pokemon_id}`: Delete a Pokémon record by ID.

### Fetch and Store Pokémon Data

- **POST** `/fetch_and_store/`: Fetch data from an external API and save it to the database.
- **GET** `/pokemon/`: Retrieve a list of Pokémon with optional parameters for search, sort, and pagination.

# Developed APIs

| SRL | METHOD | ROUTE                              | FUNCTIONALITY                                       | Required Fields                 | ACCESS         |
|-----|--------|------------------------------------|-----------------------------------------------------|---------------------------------|----------------|
| 1   | GET    | /pokemon/{pokemon_id}/             | Fetch details of a Pokémon by its ID                | Pokémon ID                      | All users      |
| 2   | POST   | /add_Pokemon/                      | Add a new Pokémon record                            | PokemonPostPutInputSchema       | admin          |
| 3   | PUT    | /update_Pokemon/{pokemon_id}/      | Update an existing Pokémon record by ID             | Pokémon ID                      | admin          |
| 4   | PATCH  | /update_Pokemon_Patch/{pokemon_id/ | Partially update a Pokémon record by ID             | Pokémon ID                      | admin          |
| 5   | DELETE | /delete_Pokemon/{pokemon_id/       | Delete a Pokémon record by ID                       | Pokémon ID                      | admin          |
| 6   | POST   | /fetch_and_store/                  | Fetch data from an external API and save it to DB   | None                            | admin          |
| 7   | GEt    | /pokemon/                          | Retrieve a list of Pokémon with optional parameters | sort, Keyword, col, limit, page | All users      |
| 8   | POST   | /register/                         | Register a new user                                 | username, password, role        | All users      |
| 9   | POST   | /login/                            | User Login                                          | username, password              | register user  |
| 10  | PUT    | /update_user/{user_id}/            | Update User by its ID                               | User ID                         | admin          |
| 11  | DELETE | /delete_user/{user_id}/            | Delete User by its ID                               | User ID                         | admin          |


## Authentication and Authorization

- Implemented using JWT or OAuth.
- Protected routes require a valid token to access, ensuring secure data management.

## Schemas

### PokemonPostPutInputSchema

- `name`: (string) Name of the pokemon.
- `type_1`: (string) Primary type of the pokemon.
- `type_2`: (string, optional) Secondary type of the pokemon.
- `total`: (integer) Total
- `hp`: (integer)
- `attack`: (integer) Attack
- `defense`: (integer) Defense
- `sp_atk`: (integer) Special attack
- `sp_def`: (integer) Special defense
- `speed`: (integer) Speed
- `generation`: (integer) Generation
- `legendary`: (boolean) Whether the pokemon is legendary or not.

### PokemonPatchInputSchema

- Allows partial updates for the following fields:
  - `name`, `type_1`, `type_2`, `total`, `hp`, `attack`, `defense`, `sp_atk`, `sp_def`, `speed`, `generation`, `legendary`.

### PokemonGetOutputSchema

## Testing

- Comprehensive test cases for all routes and functionalities.
- Test cases are organized in the `tests` folder, covering both successful and failure scenarios.
- To run tests:

   ```bash
   pytest
   ```

## Project Structure

```plaintext
src/
├── app/                     # Core application code and modules.
│   ├── auth/                # Authentication-related files (schemas, models, auth.py).
│   ├── database/            # Database setup and configuration (create_db.py, database.py).
│   ├── factories/           # Factory files for generating fake data for tests.
│   ├── pokemon/             # Pokémon-related files (schemas, models, routes.py).
│   └── tests/               # Includes conftest.py, and test cases for auth and routes.
├── main.py                  # Entry point for starting the FastAPI server.
├── changelog.md             # Documents project updates.
├── README.md                # Project overview and setup instructions.
└── requirements.txt         # Project dependencies.
```
