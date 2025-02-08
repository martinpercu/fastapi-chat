from variables import OPENAI_KEY
from fastapi import FastAPI, HTTPException
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

import os

# This import for async chat
from fastapi.responses import StreamingResponse
import asyncio

# This is for Assistant
import openai


# Get the OPENAI_KEY from environment
# OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# clientOpenAi = OpenAI(api_key=OPENAI_KEY)


# This is for Assistant
# ASSISTANT_ID = "asst_94D3ubdfJOAOKm2oPshllYRJ" #Doctor # Reemplázalo con tu ID de asistente
# ASSISTANT_ID = "asst_bhH3sUoWfxD2RQfy8dOjZ0Kb" #Kohue  # Reemplázalo con tu ID de asistente
ASSISTANT_ID = "asst_YPuH1T2frcyhAlXJZ0ibz2lg" #Napoleon  # Reemplázalo con tu ID de asistente
openai.api_key = OPENAI_KEY


# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for your app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request model
class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def home():
    return {"message": "Estamos joya adca"}

@app.get("/testopenaiapi")
async def sendApi():
    teta = str(openai)
    return {"teta es": teta}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}




class ChatRequestAssistantStream(BaseModel):
    message: str
    thread_id: str | None = None  # Optional, to maintain context


@app.post("/chat_a_stream_last")
async def chat_with_assistant(request: ChatRequestAssistantStream):
    print(request.thread_id)
    try:
        # Crear un nuevo hilo si no existe
        if not request.thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id
        else:
            thread_id = request.thread_id
        
        # Enviar el mensaje del usuario al asistente
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )
        
        # Iniciar la tarea del asistente
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Esperar a que el asistente responda
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            await asyncio.sleep(1)  # Evitar busy-waiting

        # Obtener y formatear la respuesta del asistente
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        response_message = messages.data[0].content[0].text.value
        
        async def response_stream():
            
            # Enviar el thread_id como el primer evento SSE
            yield f"event: thread_id\ndata: {thread_id}\n\n"
            
            # Se envía cada palabra como un evento SSE
            for word in response_message.split():
                # yield f"{word} "                
                yield f"data: {word}\n\n"
                # yield word
                await asyncio.sleep(0.1)  # Simula el streaming en tiempo real
        
        return StreamingResponse(response_stream(), media_type="text/event-stream")
    except Exception as e:
        print(f"🔥 ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# class TestOpenAi(BaseModel):
#     message: str
#     thread_id: str | None = None  # Opcional, para mantener contexto
#     assistant_id: str | None = None  # Opcional, para mantener contexto
#     thread_id: str | None = None  # Opcional, para mantener contexto
    
    
    
# Run the application using a command like: `uvicorn app_name:app --reload --port 3000`
