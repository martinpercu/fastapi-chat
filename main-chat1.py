from variables import OPENAI_KEY
from fastapi import FastAPI, HTTPException, Request
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

import os


# This import for async chat
from fastapi.responses import StreamingResponse
import time
import asyncio



# Get the OPENAI_KEY from environment
# OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

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
    teta = str(client)
    return {"teta es": teta}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Extract the message from the request body
        message = request.message

        # Log the input
        print("req.body =>>>", request.model_dump())
        print("message ===>", message)

        # Make the OpenAI API call
        response = client.chat.completions.create(
            model="gpt-4",  # Or use "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are an assistant. You only respond in Spanish, with Argentinian Spanish."},
                {"role": "user", "content": message},
            ]
        )

        # Extract the reply
        reply = response.choices[0].message.content
        print(reply)

        return {"reply": reply}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")




# Run the application using a command like: `uvicorn app_name:app --reload --port 3000`
