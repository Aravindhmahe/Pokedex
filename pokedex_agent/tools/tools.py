from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from functools import lru_cache
import requests
from typing import Dict, Any

POKEAPI_BASE = "https://pokeapi.co/api/v2"


def get_multiple_pokemon_data(names: list[str]) -> Dict[str, Any]:
    """Get multiple Pokémon's details by their names.
    This function is used by the Pokedex Agent to provide information about multiple Pokémon species.
    Include this function whenever if user asks for multiple Pokémon species information or their comparison.
    Strictly bounded for Pokémon species information.
    Return a list of Pokémon details for each name provided.
    If request is too generic like eg, give details of water pokemon, inform user to provide specific pokemon names.

    Args:
        names: A list of Pokémon names, such as ["pikachu", "charizard"].
    """
    if not names:
        return {}

    def fetch_details(name: str) -> Dict[str, Any]:
        try:
            return get_pokemon_details(name)
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    with ThreadPoolExecutor(max_workers=min(len(names), 5)) as executor:
        return dict(zip(names, executor.map(fetch_details, names)))

def get_pokemon_details(name: str) -> Dict[str, Any]:
    """Get a Pokémon's image, Japanese name, species category, evolution chain, cry, and stats. Use this function tool is used by the Pokedex Agent to provide information about Pokémon species. Strictly bounded for Pokémon species information.

    Args:
        name: The Pokémon's name, such as "pikachu" or "charizard".
    """

    name_clean = name.strip().lower()
    return deepcopy(_get_pokemon_details_cached(name_clean))


@lru_cache(maxsize=512)
def _get_pokemon_details_cached(name_clean: str) -> Dict[str, Any]:
    pokemon_response = requests.get(
        f"{POKEAPI_BASE}/pokemon/{name_clean}", timeout=15
    )
    pokemon_response.raise_for_status()
    pokemon = pokemon_response.json()

    species_response = requests.get(
        pokemon["species"]["url"], timeout=15
    )
    species_response.raise_for_status()
    species = species_response.json()

    evolution_response = requests.get(
        species["evolution_chain"]["url"], timeout=15
    )
    evolution_response.raise_for_status()
    evolution = evolution_response.json()

    chain_names = []

    def add_evolutions(node):
        chain_names.append(node["species"]["name"].replace("-", " ").title())
        for next_evolution in node["evolves_to"]:
            add_evolutions(next_evolution)

    add_evolutions(evolution["chain"])

    stats = {
        stat["stat"]["name"]: stat["base_stat"]
        for stat in pokemon["stats"]
    }
    names_by_language = {
        item["language"]["name"]: item["name"]
        for item in species["names"]
    }
    genera_by_language = {
        item["language"]["name"]: item["genus"]
        for item in species["genera"]
    }

    return {
        "image": pokemon["sprites"]["front_default"],
        "pokemon_name": pokemon["name"].title(),
        "japanese_name": names_by_language.get("ja-Hrkt")
            or names_by_language.get("ja"),
        "genera": genera_by_language.get("en"),
        "evolution_chain": " → ".join(chain_names),
        "audio_cries": pokemon.get("cries", {}).get("latest"),
        "stats": {
            "hp": stats["hp"],
            "height": pokemon["height"] / 10,
            "weight": pokemon["weight"] / 10,
            "attack": stats["attack"],
            "defense": stats["defense"],
            "special_attack": stats["special-attack"],
            "special_defense": stats["special-defense"],
            "speed": stats["speed"],
        },
    }
