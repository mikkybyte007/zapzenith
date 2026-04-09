from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core import start_whatsapp, send_message
from utils import typing_delay
import asyncio
from pydantic import BaseModel

app = FastAPI(title="ZapZenith Gateway", description="API do WhatsApp para integração com o Verthos.")

# Permite acesso ao Lovable de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de requisição
class MessageRequest(BaseModel):
    number: str
    text: str

@app.get("/")
async def root():
    return {"status": "ZapZenith Gateway Online!"}

@app.on_event("startup")
async def startup_event():
    # Em uma aplicação real assíncrona, deve-se usar threads ou async se a lib bloquear
    # WPP_Whatsapp é rodada de forma que start() costuma bloquear ou rodar em background.
    # Usaremos asyncio.to_thread para não bloquear o event loop do FastAPI.
    asyncio.create_task(asyncio.to_thread(start_whatsapp))

@app.post("/send-message")
async def send_whatsapp(request: MessageRequest):
    try:
        # Simulando comportamento humano antes de enviar
        await typing_delay(request.text)
        
        # Envia a mensagem invocando o motor
        response = send_message(request.number, request.text)
        return {"status": "sent", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
