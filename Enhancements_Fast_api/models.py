from database import Base, engine
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text


def create_tables():
    Base.metadata.create_all(engine)


class PokemonData(Base):
    __tablename__ = "pokemon_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(40), nullable=False)  # name should not allow NULL
    type_1 = Column(String(40), nullable=False)  # type_1 should not allow NULL
    type_2 = Column(String(40), nullable=True)  # type_2 can be NULL (optional)
    total = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    sp_atk = Column(Integer, nullable=False)
    sp_def = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    generation = Column(Integer, nullable=False)
    legendary = Column(Boolean, nullable=False)  
