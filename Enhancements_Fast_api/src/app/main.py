from fastapi import FastAPI
from src.app.auth import auth
from src.app.pokemon import routes

# Create the FastAPI app
app = FastAPI()

# Include the routers from the different route modules
app.include_router(auth.router)  # Include the auth routes
app.include_router(routes.router)  # Include the pokemon routes
