import time
import pytest
from starlette import status
from starlette.testclient import TestClient
from src.app.auth.models import UserRole
from src.app.tests.conftest import test_db, get_auth_token, get_user_token


class TestAuthRoutes:
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient, test_db, user_data, admin_data):
        self.client = client
        self.db = test_db
        self.user_data = user_data
        self.admin_data = admin_data

    # -------------------------------------
    # Test User Registration
    # -------------------------------------

    def test_register_user(self):
        # Test registration of a new user
        response = self.client.post("/auth/register", json=self.admin_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == self.admin_data["username"]
        assert data["role"] == self.admin_data["role"]
        assert "id" in data

    def test_register_existing_user(self):
        # Register the user once
        self.client.post("/auth/register", json=self.user_data)
        # Try registering the same user again
        response = self.client.post("/auth/register", json=self.user_data)
        assert response.status_code == 400
        assert response.json() == {"detail": "Username already registered"}

    # -------------------------------------
    # Test User Login
    # -------------------------------------

    def test_login_user(self, create_user):
        # Register the user for login test
        # self.client.post("/auth/login", json=self.admin_data)

        # Test login with correct credentials
        login_data = {
            "username": self.admin_data["username"],
            "password": self.admin_data["password"]
        }
        response = self.client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == self.admin_data["role"]

    def test_login_nonexistent_user(self):
        # Attempt login with invalid credentials
        invalid_login_data = {
            "username": "wronguser",
            "password": "wrongpassword"
        }
        response = self.client.post("/auth/login", data=invalid_login_data)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid username or password"}

    def test_login_user_fail_wrong_password(self):
        # Attempt login with a correct username but incorrect password
        wrong_password_login_data = {
            "username": self.admin_data["username"],
            "password": "wrongpassword"
        }
        response = self.client.post("/auth/login", data=wrong_password_login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid username or password"}

    def test_get_auth_token(self, client, get_auth_token):
        # Ensure token is not None
        assert get_auth_token is not None, "Access token should not be None"

    # ------------------------------------------
    # Update User Test Cases
    # ------------------------------------------

    def test_admin_update_user_success(self, get_auth_token):
        # Register a new user
        user_response = self.client.post("/auth/register", json=self.user_data)
        user_id = user_response.json()["id"]

        # Admin updates user information to be active and set role as admin
        headers = {"Authorization": f"Bearer {get_auth_token}"}
        update_data = {"is_active": False, "role": UserRole.admin}
        response = self.client.put(f"/auth/update_user/{user_id}", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "admin"

    def test_admin_update_user_invalid_id(self, get_auth_token):
        # Attempt to update a non-existent user
        headers = {"Authorization": f"Bearer {get_auth_token}"}
        invalid_user_id = 9999  # Assuming this ID doesn't exist
        update_data = {"is_active": True, "role": UserRole.admin}
        response = self.client.put(f"/auth/update_user/{invalid_user_id}", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found"}

    def test_non_admin_update_user_invalid_id(self, get_user_token):
        # Non-admin tries to update a non-existent user
        headers = {"Authorization": f"Bearer {get_user_token}"}
        invalid_user_id = 9999  # Assuming this ID doesn't exist
        update_data = {"is_active": True, "role": UserRole.admin}
        response = self.client.put(f"/auth/update_user/{invalid_user_id}", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Operation not permitted"}

    # ------------------------------------------
    # Delete User Test Cases
    # ------------------------------------------

    def test_admin_delete_user_success(self, get_auth_token):
        # Register a new user
        user_response = self.client.post("/auth/register", json=self.user_data)
        user_id = user_response.json()["id"]

        # Admin deletes the user
        headers = {"Authorization": f"Bearer {get_auth_token}"}
        response = self.client.delete(f"/auth/delete_user/{user_id}", headers=headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_admin_delete_user_invalid_id(self, get_auth_token):
        # Admin tries to delete a non-existent user
        headers = {"Authorization": f"Bearer {get_auth_token}"}
        invalid_user_id = 9999  # Assuming this ID doesn't exist
        response = self.client.delete(f"/auth/delete_user/{invalid_user_id}", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found"}

    def test_non_admin_delete_user_invalid_id(self, get_user_token):
        # Non-admin tries to delete a non-existent user
        headers = {"Authorization": f"Bearer {get_user_token}"}
        invalid_user_id = 9999  # Assuming this ID doesn't exist
        response = self.client.delete(f"/auth/delete_user/{invalid_user_id}", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Operation not permitted"}