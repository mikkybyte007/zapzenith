from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core import start_whatsapp, send_message, supabase, INSTANCE_ID
from utils import typing_delay
import asyncio
from pydantic import BaseModel, Field
import threading

# Segurança e Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from secure import Secure

# Configuração do Rate Limiter por IP
limiter = Limiter(key_func=get_remote_address)

# Configuração de Headers de Segurança HTTP (CSP, HSTS, X-Frame-Options, etc)
secure_headers = Secure.with_default_headers()

app = FastAPI(title="ZapZenith Gateway Enterprise", description="API do WhatsApp blindada para integração em produção.")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em prod: ["https://seu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.set_headers(response)
    return response

# Sanitização rigorosa de Payload via Pydantic
class MessageRequest(BaseModel):
    # Regex para permitir apenas números (DDI + DDD + Fone), blindando contra SQLi/Command Injection
    number: str = Field(..., pattern=r"^\d{10,15}$", description="Número de telefone apenas com dígitos")
    # Limite máximo de caracteres para evitar exaustão de memória/Buffer Overflow
    text: str = Field(..., min_length=1, max_length=4096, description="Conteúdo da mensagem")
    chat_id: str = None # UUID opcional

@app.get("/")
@limiter.limit("20/minute") # Previne flood na raiz
async def root(request: Request):
    return {"status": "ZapZenith Gateway Enterprise Online!"}

from queue_manager import start_queue_worker

@app.on_event("startup")
async def startup_event():
    start_queue_worker()
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
        
        # Atualiza a last message do chat
        supabase.table("chats").update({"last_message_preview": text[:50]}).eq("id", chat_id).execute()
    except Exception as e:
        print(f"Erro ao salvar mensagem enviada no Supabase: {e}")

@app.post("/send-message")
@limiter.limit("30/minute") # Mitiga Spam/Flood por IP de origem
async def send_whatsapp(request: Request, payload: MessageRequest):
    try:
        await typing_delay(payload.text)
        
        # O motor será invocado com dados limpos
        response = send_message(payload.number, payload.text)
        
        if payload.chat_id:
            threading.Thread(target=save_sent_message, args=(payload.number, payload.text, payload.chat_id)).start()
            
        return {"status": "sent", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno no servidor de WhatsApp. O motor pode estar desconectado.")

@app.post("/start-session")
@limiter.limit("5/minute")
async def start_session(request: Request):
    return {"status": "success", "message": "Motor WhatsApp já está rodando em background"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
