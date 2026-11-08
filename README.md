# Pokedex Agent

A FastAPI application that uses a Google ADK agent to answer Pokémon questions. For
Pokémon detail requests, the agent can call a function tool that retrieves Pokémon,
species, and evolution information from the public PokeAPI. The API returns both the
tool's structured Pokémon data and the agent's text response.

## Features

- Google ADK agent with a Pokémon details function tool
- Pokémon image, Japanese name, species category, evolution chain, cry URL, and stats
- FastAPI endpoint that can be called from Postman or another client
- Optional session reuse through the `X-Session-ID` request header
- Interactive API documentation provided by FastAPI

## Requirements

- Python 3.10 or later
- A Google Gemini API key
- Internet access for Gemini and PokeAPI requests

## Local setup

Run these commands from the repository root.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GOOGLE_API_KEY = "your-gemini-api-key"
```

If PowerShell prevents virtual environment activation, you can invoke its Python
directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:GOOGLE_API_KEY = "your-gemini-api-key"
```

Get a Gemini API key from Google AI Studio. Keep the key private; do not commit it to
the repository. The environment variable must be set in the same terminal session
that runs the API.

## Run the API

From the repository root, with the virtual environment active and the API key set:

```powershell
python -m uvicorn pokedex_agent.api:app --reload
```

The server listens at `http://127.0.0.1:8000`. Leave this terminal running while
using the API. Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Call the API from Postman

Create a request with:

- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/getPokemonDetails`
- **Body:** **raw** → **JSON**
- **Header:** `Content-Type: application/json`

Example request body:

```json
{
  "user_query": "Tell me about Pikachu"
}
```

The response includes the session ID, the Pokémon data returned by the tool (if the
agent called it), and the agent's text response:

```json
{
  "status": 200,
  "session_id": "session-id-returned-by-the-server",
  "response": {
    "pokemon_card": {
      "image": "https://...",
      "pokemon_name": "Pikachu",
      "japanese_name": "ピカチュウ",
      "genera": "Mouse Pokémon",
      "evolution_chain": "Pichu → Pikachu → Raichu",
      "audio_cries": "https://...",
      "stats": {
        "hp": 35,
        "height": 0.4,
        "weight": 6.0,
        "attack": 55,
        "defense": 40,
        "special_attack": 50,
        "special_defense": 50,
        "speed": 90
      }
    },
    "response_text": "Pikachu is an Electric-type Pokémon..."
  }
}
```

Values and the agent's wording depend on the request. When the agent does not call
the Pokémon tool, `pokemon_card` may be `null`.

### Reuse a conversation session

The first request creates a session and returns its `session_id`. To continue that
conversation, send another request to the same endpoint and include this header:

```text
X-Session-ID: session-id-returned-by-the-server
```

Omit the header to start a new session. Sessions are held in memory, so they are lost
when the server stops or restarts.

## Project layout

```text
README.md
requirements.txt
pokedex_agent/
    agent.py                 # ADK agent configuration and instructions
    api.py                   # FastAPI app, endpoint, runner, and sessions
    schema/
        pokemon_schema.py    # Pydantic models for Pokémon data
    tools/
        tools.py             # PokeAPI-backed Pokémon details tool
```

## Data source

Pokémon data is retrieved from the public [PokeAPI](https://pokeapi.co/). The API
requests Pokémon, species, and evolution-chain data. Gemini generates the agent's
text response and can decide when to call the registered tool.
