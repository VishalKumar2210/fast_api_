# Changelog

## [27-09-24](https://github.com/VishalKumar2210/fast_api_/pull/2/files)
### Added
- Bulk insert and GET route with the following features:
  - Input and output schemas.
  - `bulk_insert_mappings` function.
  - Sorting based on the 'id' column in either ascending or descending order, based on user input.
  - Search functionality to find a keyword in a specified column, defaulting to the 'name' column.
  - Pagination for results with a configurable limit per page, defaulting to a specified integer.

## [01-10-24](https://github.com/VishalKumar2210/fast_api_/pull/2/commits/e34a09faaff9b7a1644e8daf552d2cfa144bc472)
### Fixed
- **File**: `models.py`
  - Removed commented code.
  - Updated column definitions to specify whether each column accepts "NULL" or not.

### Added
- **File**: `pokemon.sql`
  - Added SQL queries for table creation, data insertion, and record deletion.

### Added and Fixed
- **File**: `main.py`
  - Added `sort_order` in `get_all_pokemon` routes, accepting only `["asc", "desc"]` as inputs, defaulting to `"asc"`.
  - Fixed the `fetch_and_store` route by removing `db.refresh` as it is not necessary unless multiple sources are updating the database simultaneously.

## [19-10-24](https://github.com/VishalKumar2210/fast_api_/pull/3/commits/13ec4d2f40ce440c965bfaa6113b15a8f71ea264)
### Added
- **File**: `auth.py`
  - Added routes for user registration and login, returning a JWT token upon successful login.
  - Functionality to check if a user is authenticated.
  - Role-based access with `role_checker` to differentiate between admin and other users.
  - Admin-only routes for updating and deleting users.
  - Implemented core authentication logic, including token creation, password hashing, password verification, and user authentication.

### Fixed
- **File**: `main.py` (renamed to `routes.py`)
  - Added validation for the `sort_order` parameter in routes.
  - Removed unnecessary code.
  - Implemented role-based authentication across all routes.

### Added and Fixed
- **File**: `schemas.py`
  - Updated `PokemonPostPutInputSchema` to make `type_2` optional.
  - Added authentication schemas:
    - `UserCreate` schema with `username`, `password`, and `role` fields.
    - `UserResponse` schema to show user data.
    - `UserUpdate` schema for updating user data.
    - Login token schema for authentication.

### Added
- **File**: `models.py`
  - Added `User` table to support authentication and authorization.
  - Added `UserRole` to define user roles like `admin`, `user`, and `moderator`.

## [14-11-24] ()
### Added
- Organized the FastAPI project into a structured folder format for improved maintainability and scalability.

### Project Structure
- `src/`: Contains the main application directory and associated files.
  - `app/`: Houses all core application code and modules.
    - `auth/`: Contains all authentication-related files, including schemas, models, and `auth.py`.
    - `database/`: Includes database setup and configuration files, such as `create_db.py` and `database.py`.
    - `factories/`: Contains factory files for generating fake data for test cases.
    - `pokemon/`: Stores all Pokémon-related files, including schemas, models, and `routes.py`.
  - `tests/`: Includes `conftest.py`, test cases for authentication (`auth`), and test cases for routes (`routes.py`).
  - `main.py`: The main application entry point for starting the FastAPI server.
- **Root Files**:
  - `changelog.md`: This file, documenting project updates.
  - `README.md`: Provides an overview and setup instructions for the project.
  - `requirements.txt`: Lists all dependencies required to run the project.

### Changed
- Updated import paths to reflect the new directory structure.
- Restructured authentication and Pokémon-related code into dedicated subdirectories.

### Updated
- **File**: `database.py`
  - Added dependency for database sessions to ensure sessions close after use in routes.

### Updated
- **File**: `auth.py`
  - Changed `SECRET_KEY` to be accessed from environment variables using `os.getenv("SECRET_KEY", "your_default_secret_key")`, improving security.

## Tests
### Added
- Created a `tests/` directory to organize all test cases.
  - **File**: `conftest.py`
    - Configures fixtures and setup for testing, including database connections and cleanup.
  - **File**: `test_case_routes.py`
    - Contains test cases for all routes, covering both pass and fail scenarios with authorization checks.
  - **File**: `test_auth.py`
    - Includes test cases for user authentication and management:
      - **User Registration**: Tests successful and unsuccessful registrations.
      - **User Login**: Tests correct login handling and failure cases.
      - **User Update**: Tests updating user information.
      - **User Deletion**: Tests deleting a user account.

### Added
- **File**: `.pre-commit-config.yaml`
  - Configured pre-commit hooks for automated code checks to enforce code quality and formatting standards before commits.
