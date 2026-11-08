from google.adk.agents import Agent

root_agent = Agent(
    name="pokedex_agent",
    model="gemini-3.8-flash",
    description="An agent that provides information about Pokémon.",
    instruction="You are a helpful assistant that provides information about Pokémon species, types, abilities, and related topics.",
)
