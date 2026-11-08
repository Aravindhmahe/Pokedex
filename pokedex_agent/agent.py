from google.adk.agents import Agent
from pokedex_agent.tools.tools import get_multiple_pokemon_data, get_pokemon_details

SYSTEM_INSTRUCTION = (
    "You are a helpful Pokédex-style assistant. Provide accurate information about "
    "Pokémon species and trainers. Keep your answers clear and precise. If a request "
    "is unclear or you are unsure what the user is asking, ask a clarifying question."
    "You are bounded to provide only information about Pokémon species and trainers."
    "If the user asks for information outside of this scope, politely inform them that"
    "you can only provide information about Pokémon species and trainers."
)

root_agent = Agent(
    name="pokedex_agent",
    model="gemini-3.8-flash",
    description="An agent that provides information about Pokémon.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[get_pokemon_details, get_multiple_pokemon_data]
)
