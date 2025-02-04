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


from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI



# Get the OPENAI_KEY from environment
# OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
client = ChatOpenAI(api_key=OPENAI_KEY)

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

        # Make the OpenAI API call
        prompt = PromptTemplate(
            template="Answer the user query. \n{format_instructions}\n{query}",
            input_variables=["query"],
            partial_variables={
                "format_instructions": JsonOutputParser().get_format_instructions()
            },
        )

        chain = prompt | client | JsonOutputParser()

        response = chain.invoke({"query": message})

        # Streaming the response
        async def stream_response():
            try:
                async for chunk in chain.astream({"query": message}):
                    yield f"{chunk}\n".encode("utf-8")  # Send each chunk as a new line
            except Exception as e:
                print(f"Error streaming response: {e}")
                yield f"Error: {e}\n".encode("utf-8")


        # async def stream_response():
        #     async for chunk in chain.astream({"query": message}):
        #         yield chunk.encode("utf-8")


        # async def stream_response():
        #     try:
        #         for s in chain.stream({"query": message}):
        #             yield str(s).encode('utf-8')
        #             time.sleep(0.3)
        #     except Exception as e:
        #         print(f"Error: {e}")
        
        # # Streaming the response
        # async def stream_response():
        #     for s in chain.stream({"query": message}):
        #         yield s
        #         time.sleep(0.3)

        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")





# Run the application using a command like: `uvicorn app_name:app --reload --port 3000`
