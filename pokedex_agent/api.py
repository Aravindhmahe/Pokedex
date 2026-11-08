import uuid
from google.genai import types
from pokedex_agent import agent
from google.adk.runners import Runner
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.sessions import InMemorySessionService

app = FastAPI(
    title="Pokedex Agent",
    description="An API for interacting with the Pokedex Agent.",
    version="1.0.0"
);

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_NAME = "pokedex_agent"
USER_ID = "user"

session_service = InMemorySessionService()
runner = Runner(
    agent=agent.root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

@app.post('/getPokemonDetails', description="Get details of a Pokemon based on user query.")
async def chat_with_pokedex(
    user_query: dict[str, str],
    session_id: str | None = Header(default=None, alias="X-Session-ID"),
):
    query_text = user_query.get("user_query", "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if session_id is None:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )
    else:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )
        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Omit X-Session-ID to create a new session.",
            )

    message = types.Content(
        role="user",
        parts=[types.Part(text=query_text)],
    )

    description = ""
    pokemon_card_data = None  # To hold the structured tool response

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if event.content:
            for part in event.content.parts:
                # Capture the actual data returned by your tool function
                if part.function_response:
                    pokemon_card_data = part.function_response.response

        if event.is_final_response() and event.content:
            description = "\n".join(
                part.text for part in event.content.parts if part.text
            )

    return {
        "status": 200,
        "session_id": session_id,
        "response": {
            "pokemon_card": pokemon_card_data,
            "description": description,
        },
    }