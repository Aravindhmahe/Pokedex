import requests
from typing import Dict, Any

POKEAPI_BASE = "https://pokeapi.co/api/v2"

def get_pokemon_details(name: str) -> Dict[str, Any]:
    """Get a Pokémon's image, Japanese name, species category, evolution chain, cry, and stats. Use this function tool is used by the Pokedex Agent to provide information about Pokémon species. Strictly bounded for Pokémon species information.

    Args:
        name: The Pokémon's name, such as "pikachu" or "charizard".
    """

    name_clean = name.strip().lower()

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

