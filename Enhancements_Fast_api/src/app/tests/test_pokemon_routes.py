import pytest
from fastapi.testclient import TestClient
from src.app.tests.conftest import override_get_db


class TestPokemonRoutes:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient, get_auth_token):
        self.client = client
        self.db = override_get_db
        self.token = get_auth_token
        print(self.token)

    def test_get_pokemon_by_id_success(self, create_pokemon):
        headers = {"Authorization": f"Bearer {self.token}"}

        pokemon = create_pokemon()
        response = self.client.get(f"/pokemon/{pokemon.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == pokemon.name

    def test_get_pokemon_by_id_failure(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        pokemon_id = 99999
        response = self.client.get(f"/pokemon/{pokemon_id}", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Pokemon not found."

    def test_add_pokemon_success(self, valid_pokemon_data):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.post("/pokemon", json=valid_pokemon_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == valid_pokemon_data["name"]

    def test_add_pokemon_failure(self, invalid_pokemon_data):
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self.client.post("/pokemon", json=invalid_pokemon_data, headers=headers)
        assert response.status_code == 422
        assert response.json()["detail"] is not None

    def test_update_pokemon_success(self, create_pokemon):

        initial_pokemon = create_pokemon()

        updated_data = {
            "name": "test_update_pokemon_success",
            "type_1": "Electric",
            "type_2": None,
            "total": 480,
            "hp": 60,
            "attack": 90,
            "defense": 55,
            "sp_atk": 90,
            "sp_def": 80,
            "speed": 110,
            "generation": 1,
            "legendary": False
        }

        response = self.client.put(f"/pokemon/{initial_pokemon.id}", json=updated_data,
                                   headers={"Authorization": f"Bearer {self.token}"}
                                   )

        assert response.status_code == 202
        updated_pokemon = response.json()
        assert updated_pokemon["name"] == "test_update_pokemon_success"

    def test_update_pokemon_failure(self, create_pokemon):
        pokemon_id = 99999
        updated_data = {
            "name": "test_update_pokemon_success",
            "type_1": "Electric",
            "type_2": None,
            "total": 480,
            "hp": 60,
            "attack": 90,
            "defense": 55,
            "sp_atk": 90,
            "sp_def": 80,
            "speed": 110,
            "generation": 1,
            "legendary": False
        }

        response = self.client.put(
            f"/pokemon/{pokemon_id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Pokemon with this id does not exist."

    def test_update_pokemon_patch(self, create_pokemon):
        initial_pokemon = create_pokemon()
        patch_data = {
            "name": "test_update_pokemon_patch",
            "type_1": "Water",
            "type_2": "Poison",
            "total": 310,
            "hp": 30,
            "attack": 35,
            "defense": 30,
            "sp_atk": 100,
            "sp_def": 35,
            "speed": 80,
            "generation": 1,
            "legendary": False,
        }

        response = self.client.patch(
            f"/pokemon/{initial_pokemon.id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 200
        patched_pokemon = response.json()
        assert patched_pokemon["hp"] == 30

    def test_update_nonexistent_pokemon_patch(self, create_pokemon):
        pokemon_id = 99999
        patch_data = {
            "name": "test_update_pokemon_patch",
            "type_1": "Water",
            "type_2": "Poison",
            "total": 310,
            "hp": 30,
            "attack": 35,
            "defense": 30,
            "sp_atk": 100,
            "sp_def": 35,
            "speed": 80,
            "generation": 1,
            "legendary": False,
        }

        response = self.client.patch(
            f"/pokemon/{pokemon_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == f"Pokemon with id {pokemon_id} doesn't exist..."

    def test_delete_pokemon(self, create_pokemon):
        initial_pokemon = create_pokemon()

        response = self.client.delete(
            f"/pokemon/{initial_pokemon.id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 204

    def test_delete_not_existing_pokemon(self):
        pokemon_id = 99999

        response = self.client.delete(
            f"/pokemon/{pokemon_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        assert response.status_code == 404
