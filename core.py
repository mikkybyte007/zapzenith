import os
import asyncio
import threading
from WPP_Whatsapp import Create
from supabase import create_client, Client
from dotenv import load_dotenv

# Resiliência
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("Aviso crítico de segurança: SUPABASE_URL e SUPABASE_KEY não configurados no .env")

wa_client = None
INSTANCE_ID = os.environ.get("INSTANCE_ID", None)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def update_instance_status(status: str, qrcode_base64: str = None):
    if not supabase or not INSTANCE_ID:
        return
    data = {"status": status}
    if qrcode_base64 is not None:
        data["qrcode_base64"] = qrcode_base64
    supabase.table("whatsapp_instances").update(data).eq("id", INSTANCE_ID).execute()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
def handle_incoming_message(sender_id, text_body):
    """
    Insere mensagem e cria chat se não existir (Com retry e backoff)
    """
    if not supabase or not INSTANCE_ID:
        return

    phone_number = sender_id.replace('@c.us', '')
    
    # Previne falhas transacionais
    chat_response = supabase.table("chats").select("id, status").eq("contact_number", phone_number).eq("instance_id", INSTANCE_ID).execute()
    
    chat_id = None
    if len(chat_response.data) > 0:
        chat_id = chat_response.data[0]["id"]
        # Atualiza a preview e força chat a reabrir se estiver CLOSED
        updates = {"last_message_preview": text_body[:50]}
        if chat_response.data[0]["status"] == "CLOSED":
            updates["status"] = "OPEN"
            
        supabase.table("chats").update(updates).eq("id", chat_id).execute()
    else:
        new_chat = supabase.table("chats").insert({
            "instance_id": INSTANCE_ID,
            "contact_name": phone_number,
            "contact_number": phone_number,
            "last_message_preview": text_body[:50],
            "status": "OPEN"
        }).execute()
        chat_id = new_chat.data[0]["id"]

    supabase.table("messages").insert({
        "chat_id": chat_id,
        "instance_id": INSTANCE_ID,
        "sender": "CUSTOMER",
        "content": text_body
    }).execute()

def on_message(message):
    sender = message.get('from', 'Desconhecido')
    body = message.get('body', '')
    
    # Tratamento Edge Case: Mensagem sem texto (Apenas mídia não suportada)
    if not body:
        print(f"[{sender}] Ignorando mensagem multimídia ou sem texto.")
        return
        
    threading.Thread(target=handle_incoming_message, args=(sender, body)).start()

def on_qr_code(qrCode, asciiQR, attempt, urlCode):
    print(f"QR Code recebido (Tentativa {attempt})")
    # Envia base64 para o Supabase
    try:
        update_instance_status("QRCODE", qrcode_base64=urlCode)
    except Exception as e:
        print("Falha ao salvar QR Code no banco", e)

def on_status_find(statusSession, session):
    print("Event Status Session:", statusSession)
    
    if statusSession in ["isLogged", "inChat", "SUCCESS"]:
        try:
            update_instance_status("CONNECTED", qrcode_base64="")
        except:
            pass
    
    # Circuit Breaker: Desconexão ou Queda do Browser
    if statusSession in ["autocloseCalled", "browserClose", "desconnectedMobile"]:
        print("Alerta: Dispositivo desconectado ou sessão caiu. Sinalizando Fallback...")
        try:
            update_instance_status("DISCONNECTED", qrcode_base64="")
        except:
            pass

def start_whatsapp():
    global wa_client
    
    if supabase and INSTANCE_ID:
        try:
            res = supabase.table("whatsapp_instances").select("id").eq("id", INSTANCE_ID).execute()
            if len(res.data) == 0:
                supabase.table("whatsapp_instances").insert({"id": INSTANCE_ID, "instance_name": "Instância 1"}).execute()
        except:
            pass

    wa_client = Create(
        session="bot_session", 
        catchQR=on_qr_code, 
        statusFind=on_status_find,
        logQR=True
    )
    
    wa_client.start()
    wa_client.onMessage(on_message)
    print("WhatsApp motor ligado. Monitorando eventos...")

def send_message(number: str, text: str):
    if wa_client is None:
        raise Exception("Cliente WhatsApp está offline.")
    
    if not number.endswith("@c.us"):
        number = f"{number}@c.us"
        
    result = wa_client.sendText(number, text)
    return result
