from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core import start_whatsapp, send_message, supabase, INSTANCE_ID
from utils import typing_delay
import asyncio
from pydantic import BaseModel
import threading

app = FastAPI(title="ZapZenith Gateway", description="API do WhatsApp para integração com o Verthos.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    number: str
    text: str
    chat_id: str = None # Opcional, para atrelar a um chat no banco

@app.get("/")
async def root():
    return {"status": "ZapZenith Gateway Online!"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(asyncio.to_thread(start_whatsapp))

def save_sent_message(number: str, text: str, chat_id: str):
    if not supabase or not INSTANCE_ID or not chat_id:
        return
    try:
        supabase.table("messages").insert({
            "chat_id": chat_id,
            "instance_id": INSTANCE_ID,
            "sender": "ATTENDANT",
            "content": text
        }).execute()
        
        # Atualiza a last message
        supabase.table("chats").update({"last_message_preview": text[:50]}).eq("id", chat_id).execute()
    except Exception as e:
        print(f"Erro ao salvar mensagem enviada no Supabase: {e}")

@app.post("/send-message")
async def send_whatsapp(request: MessageRequest):
    try:
        await typing_delay(request.text)
        
        response = send_message(request.number, request.text)
        
        # Se for do painel, salva no banco de forma assíncrona
        if request.chat_id:
            threading.Thread(target=save_sent_message, args=(request.number, request.text, request.chat_id)).start()
            
        return {"status": "sent", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-session")
async def start_session():
    # Apenas retorna sucesso pois o startup_event já liga o motor
    return {"status": "success", "message": "Motor WhatsApp já está rodando em background"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
