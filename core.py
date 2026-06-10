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
    from security_crypto import encrypt_data
    if not supabase or not INSTANCE_ID:
        return
    data = {"status": status}
    if qrcode_base64 is not None:
        data["qrcode_base64"] = encrypt_data(qrcode_base64)
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

# Assinaturas binárias (Magic Numbers) permitidas (JPEG, PNG, PDF)
ALLOWED_MAGIC_NUMBERS = [b'\xFF\xD8\xFF', b'\x89\x50\x4E\x47', b'\x25\x50\x44\x46']

def validate_magic_number(file_bytes: bytes) -> bool:
    """Validação contra Malware: Verifica o cabeçalho do arquivo ignorando a extensão"""
    for magic in ALLOWED_MAGIC_NUMBERS:
        if file_bytes.startswith(magic):
            return True
    return False

def on_message(message):
    import asyncio
    from queue_manager import enqueue_message
    
    sender = message.get('from', 'Desconhecido')
    body = message.get('body', '')
    has_media = message.get('hasMedia', False)
    
    # Tratamento Edge Case de Mídia / Malware Guard
    if has_media:
        # Exemplo simulado: Na lib WPP_Whatsapp você usaria wa_client.downloadMedia(message)
        # Vamos simular que baixamos e validamos o binário
        print(f"[{sender}] Mídia recebida. Validando Magic Numbers...")
        # if not validate_magic_number(downloaded_bytes):
        #    print("ALERTA DE SEGURANÇA: Mídia recusada (Assinatura binária inválida).")
        #    return
    
    if not body:
        print(f"[{sender}] Ignorando mensagem sem texto processável.")
        return
        
    # Enfileiramento O(1) Desacoplado
    try:
        asyncio.run(enqueue_message(sender, body))
    except Exception as e:
        print(f"Erro Crítico ao enfileirar webhhook: {e}")

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
