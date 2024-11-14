import pytest
from starlette.testclient import TestClient
from src.app.main import app
# from src.app.pokemon.routes import app
from src.app.database.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.app.auth.models import UserRole
from src.app.factories.factory import PokemonFactory
from passlib.context import CryptContext

# Database setup
TEST_DATABASE_URL = "postgresql://vishal.chaurasiya:Password@localhost/test_pokemon"

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Dependency override for using the test database in the app
def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Apply the dependency override to use the test database
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# Fixture to set up and tear down the test database schema before and after tests
@pytest.fixture(scope="module")
def test_db():
    # Create all tables in the test database
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests are completed
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_data():
    return {
        "username": "admin_user",
        "password": "adminpass",
        "role": UserRole.admin
    }


@pytest.fixture
def user_data():
    return {
        "username": "test_user",
        "password": "testpass",
        "role": UserRole.user
    }


@pytest.fixture()
def create_user(client, test_db, admin_data):
    response = client.post("/auth/register", json=admin_data)
    return response.json()


@pytest.fixture
def get_auth_token(client, create_user, admin_data):
    # client.post("/auth/register", json=admin_data)  # Register admin
    response = client.post("/auth/login", data={"username": admin_data["username"], "password": admin_data["password"]})
    return response.json().get("access_token")


@pytest.fixture
def get_user_token(client, user_data):
    client.post("/auth/register", json=user_data)  # Register user
    response = client.post("/auth/login", data={"username": user_data["username"], "password": user_data["password"]})
    return response.json().get("access_token")


@pytest.fixture
def valid_pokemon_data():
    return {
        "name": "Pikachu",
        "type_1": "Electric",
        "type_2": None,
        "total": 320,
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "sp_atk": 50,
        "sp_def": 50,
        "speed": 90,
        "generation": 1,
        "legendary": False
    }


@pytest.fixture
def invalid_pokemon_data():
    return {
        "name": "Pikachu",
        "type_1": "Electric",
        "type_2": None,
        "total": 320,
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "sp_atk": 50,
        # "sp_def": 50,
        "speed": 90,
        "generation": 111,
        "legendary": False
    }


@pytest.fixture(scope="function")
def db() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def create_pokemon(db: Session):
    PokemonFactory.set_session(db)

    def _create_pokemon(**kwargs):
        pokemon_data = PokemonFactory.create_pokemon(**kwargs)
        return pokemon_data

    return _create_pokemon
