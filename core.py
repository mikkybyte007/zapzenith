import os
import asyncio
import threading
from WPP_Whatsapp import Create
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuração Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("Aviso: SUPABASE_URL e SUPABASE_KEY não configurados no .env")

# A instância global do client/wa será armazenada aqui
wa_client = None

# UUID da Instância (Defina no .env ou hardcoded para teste)
INSTANCE_ID = os.environ.get("INSTANCE_ID", None)

def update_instance_status(status: str, qrcode_base64: str = None):
    if not supabase or not INSTANCE_ID:
        return
    try:
        data = {"status": status}
        if qrcode_base64 is not None:
            data["qrcode_base64"] = qrcode_base64
        supabase.table("whatsapp_instances").update(data).eq("id", INSTANCE_ID).execute()
    except Exception as e:
        print(f"Erro ao atualizar status da instância no Supabase: {e}")

def handle_incoming_message(sender_id, text_body):
    """
    Insere a mensagem recebida no Supabase, lidando com a tabela de chats.
    """
    if not supabase or not INSTANCE_ID:
        print("Supabase não configurado. Mensagem recebida:", text_body)
        return

    phone_number = sender_id.replace('@c.us', '')
    
    try:
        # 1. Verifica se existe o chat
        chat_response = supabase.table("chats").select("id").eq("contact_number", phone_number).eq("instance_id", INSTANCE_ID).execute()
        
        chat_id = None
        if len(chat_response.data) > 0:
            chat_id = chat_response.data[0]["id"]
            # Atualiza o last_message
            supabase.table("chats").update({"last_message_preview": text_body[:50]}).eq("id", chat_id).execute()
        else:
            # Cria novo chat
            new_chat = supabase.table("chats").insert({
                "instance_id": INSTANCE_ID,
                "contact_name": phone_number,
                "contact_number": phone_number,
                "last_message_preview": text_body[:50],
                "status": "OPEN"
            }).execute()
            chat_id = new_chat.data[0]["id"]

        # 2. Insere a mensagem
        supabase.table("messages").insert({
            "chat_id": chat_id,
            "instance_id": INSTANCE_ID,
            "sender": "CUSTOMER",
            "content": text_body
        }).execute()
        print(f"Mensagem salva no banco com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar mensagem no Supabase: {e}")

def on_message(message):
    sender = message.get('from', 'Desconhecido')
    body = message.get('body', '')
    
    if not body:
        return
        
    print(f"Nova mensagem recebida de {sender}: {body}")
    
    threading.Thread(target=handle_incoming_message, args=(sender, body)).start()

def on_qr_code(qrCode, asciiQR, attempt, urlCode):
    print("QR Code recebido!")
    # qrCode (o primeiro argumento na lib WPP) normalmente é a string data URI ou raw
    # Vamos salvar no supabase para o frontend ler
    update_instance_status("QRCODE", qrcode_base64=urlCode)

def on_status_find(statusSession, session):
    print("Status Session:", statusSession)
    if statusSession == "isLogged" or statusSession == "inChat" or statusSession == "SUCCESS":
        update_instance_status("CONNECTED", qrcode_base64="")

def start_whatsapp():
    global wa_client
    
    # Se houver instance_id, tenta registrar no DB se não existir
    if supabase and INSTANCE_ID:
        try:
            res = supabase.table("whatsapp_instances").select("id").eq("id", INSTANCE_ID).execute()
            if len(res.data) == 0:
                supabase.table("whatsapp_instances").insert({"id": INSTANCE_ID, "instance_name": "Instância 1"}).execute()
        except:
            pass

    # Passamos as funções callback para a lib WPP
    wa_client = Create(
        session="bot_session", 
        catchQR=on_qr_code, 
        statusFind=on_status_find,
        logQR=True
    )
    wa_client.start()
    
    wa_client.onMessage(on_message)
    print("WhatsApp motor iniciado com sucesso.")

def send_message(number: str, text: str):
    if wa_client is None:
        raise Exception("Cliente WhatsApp não está inicializado.")
    
    if not number.endswith("@c.us"):
        number = f"{number}@c.us"
        
    result = wa_client.sendText(number, text)
    return result
