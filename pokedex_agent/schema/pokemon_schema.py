from pydantic import BaseModel

class PokemonStats(BaseModel):
    hp: int
    height: float
    weight: float
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

class PokemonResponse(BaseModel):
    image: str | None
    pokemon_name: str
    japanese_name: str | None
    genera: str | None
    evolution_chain: str | None
    audio_cries: str | None
    stats: PokemonStats
