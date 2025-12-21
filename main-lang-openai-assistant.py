from variables import OPENAI_KEY
from fastapi import FastAPI, HTTPException, Request
from typing import Optional, AsyncGenerator

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


from fastapi import Response
# from fastapi.responses import StreamingResponse
from fastapi.requests import Request
from fastapi.responses import JSONResponse
# from fastapi.responses import StreamingResponse
from fastapi.responses import Response
from fastapi import HTTPException
import asyncio
import json


# This is for Assistant
import openai


# Get the OPENAI_KEY from environment
# OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client (ojo este es de Langchain)
client = ChatOpenAI(api_key=OPENAI_KEY)


clientOpenAi = OpenAI(api_key=OPENAI_KEY)

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
    teta = str(client)
    return {"teta es": teta}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/chat-old")
async def chat(request: ChatRequest):
    try:
        # Extract the message from the request body
        message = request.message
        # print(message)

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

        print(StreamingResponse(stream_response(), media_type="text/plain"))

        return StreamingResponse(stream_response(), media_type="text/plain")
        # return StreamingResponse(stream_response(), media_type="text/event-stream")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")
    

# @app.post("/chat")
# async def chat(request: ChatRequest):
#     try:
#         # Process and generate response
#         message = request.message
#         prompt = f"Answer the user query. \n{message}"

#         # Simulate streaming the response (replace this with actual logic)
#         async def stream_response() -> AsyncGenerator[str, None]:
#             for chunk in prompt.split():
#                 yield f"{chunk}\n"  # Simulate chunks of text
#                 await asyncio.sleep(1)  # Simulate delay between chunks

#         return StreamingResponse(stream_response(), media_type="text/plain")

#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Something went wrong!")
    
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Process and generate response
        message = request.message
        prompt = f"Answer the user query. \n{message}"

        # Simulate streaming the response (replace this with actual logic)
        async def stream_response() -> AsyncGenerator[bytes, None]:
            for chunk in prompt.split():
                yield chunk.encode()  # Simulate chunks of text
                await asyncio.sleep(1)  # Simulate delay between chunks

        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")



@app.post("/chato")
async def chato(request: ChatRequest):
    try:
        # Process and generate response
        message = request.message
        prompt = f"Answer the user query. \n{message}"

        # Simulate streaming the response (replace this with actual logic)
        async def stream_response() -> AsyncGenerator[bytes, None]:
            for chunk in prompt.split():
                yield chunk.encode()  # Simulate chunks of text
                await asyncio.sleep(1)  # Simulate delay between chunks
        
        print(StreamingResponse(stream_response(), media_type="text/event-stream"))
        return StreamingResponse(stream_response(), media_type="text/event-stream")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")



@app.post("/chatwip")
async def chatwip(request: ChatRequest):
    try:
        message = request.message        
        print(message)
        
        parser = JsonOutputParser()
        
        prompt = PromptTemplate(
            template = 'Answer the user query. \n{format_instructions}\n{query}',
            input_variables = ['query'],
            partial_variables = { 'format_instructions': parser.get_format_instructions()}
        )
        
        chain = prompt | client | parser
        
        response = chain.invoke({"query": message})
        
        async def stream_response():
            async for chunk in client.astream(message):
                print(chunk)
                yield chunk.content.encode()  # Yield the chunk content
                await asyncio.sleep(0.13)  # Simulate delay between chunks
                
        return StreamingResponse(stream_response(), media_type="text/event-stream")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")




class ChatRequestAssistant(BaseModel):
    message: str
    thread_id: str | None = None  # Opcional, para mantener contexto


@app.post("/chat_a")
async def chat_with_assistant(request: ChatRequestAssistant):
    try:
        # Si no hay un thread_id, crear uno nuevo
        if not request.thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id
        else:
            thread_id = request.thread_id
        
        # Enviar mensaje al asistente
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )

        # Ejecutar la tarea del asistente
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Esperar respuesta del asistente
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break

        # Obtener respuesta del asistente
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        response_message = messages.data[0].content[0].text.value

        return {"thread_id": thread_id, "response": response_message}

    except Exception as e:
        print(f"🔥 ERROR: {str(e)}")  # Mostrar error en la terminal
        raise HTTPException(status_code=500, detail=str(e))




class ChatRequestAssistantStream(BaseModel):
    message: str
    thread_id: str | None = None  # Optional, to maintain context

async def stream_assistant_response(thread_id: str):
    try:
        # Start the assistant task
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for the assistant's response
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            await asyncio.sleep(1)  # Avoid busy-waiting

        # Stream the response message
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        response_message = messages.data[0].content[0].text.value
        
        for word in response_message.split():
            yield word + " "
            await asyncio.sleep(0.05)  # Simulate real-time streaming
    except Exception as e:
        yield f"Error: {str(e)}"

@app.post("/chat_a_stream")
async def chat_with_assistant(request: ChatRequestAssistantStream):
    try:
        # Create a new thread if none exists
        if not request.thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id
        else:
            thread_id = request.thread_id
        
        # Send user message to the assistant
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )
        
        return StreamingResponse(stream_assistant_response(thread_id), media_type="text/plain")
    except Exception as e:
        print(f"🔥 ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))








class ChatRequestAssistantStream(BaseModel):
    message: str
    thread_id: str | None = None  # Optional, to maintain context


@app.post("/chat_a_stream_2")
async def chat_with_assistant(request: ChatRequestAssistantStream):
    try:
        # Create a new thread if none exists
        if not request.thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id
        else:
            thread_id = request.thread_id
        
        # Send user message to the assistant
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )
        
        # Start the assistant task
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for the assistant's response
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            await asyncio.sleep(1)  # Avoid busy-waiting

        # Stream the response message
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        response_message = messages.data[0].content[0].text.value
        
        async def response_stream():
            for word in response_message.split():
                yield word + " "
                await asyncio.sleep(0.05)  # Simulate real-time streaming
        
        return StreamingResponse(response_stream(), media_type="text/plain")
    except Exception as e:
        print(f"🔥 ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))











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














class TestOpenAi(BaseModel):
    message: str
    thread_id: str | None = None  # Opcional, para mantener contexto
    assistant_id: str | None = None  # Opcional, para mantener contexto
    thread_id: str | None = None  # Opcional, para mantener contexto
    

@app.post("/test_openai")
async def test_openai(request: TestOpenAi):
    try:
        print(request)
        assisID = request.assistant_id
        print(assisID)
        
        # thread_message = clientOpenAi.beta.threads.messages.create(
        # "thread_abc123",
        # role="user",
        # content="How does AI work? Explain it in simple terms.",
        # )
        # print(thread_message)
        
        my_assistant = clientOpenAi.beta.assistants.retrieve(assisID)
        print(my_assistant)
        
        
        # my_assistants = clientOpenAi.beta.assistants.list(
        #     order="desc",
        #     limit="20",
        # )
        # print(my_assistants.data)
        
        run = clientOpenAi.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id=assisID
        )

        print(run)
    
        
        # async def stream_response():
        #     async for chunk in client.astream(message):
        #         print(chunk)
        #         yield chunk.content.encode()  # Yield the chunk content
        #         await asyncio.sleep(0.13)  # Simulate delay between chunks

        # return StreamingResponse(stream_response(), media_type="text/event-stream")
                
        return 'tamos'

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong!")
    
    
    
# Run the application using a command like: `uvicorn app_name:app --reload --port 3000`
