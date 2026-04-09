from WPP_Whatsapp import Create
import asyncio

# A instância global do client/wa será armazenada aqui
wa_client = None

import requests
import json
import asyncio

# Webhook do Supabase gerado pelo Lovable
WEBHOOK_URL = "https://lbkzdycnqrgvbuxoljvt.supabase.co/functions/v1/whatsapp-webhook?empresa_id=caaa1ef3-6e8c-4fdd-9388-69d95c4a9458"

def forward_to_webhook(sender_id, text_body):
    """
    Envia a mensagem recebida para o Webhook do Supabase, 
    imitando a estrutura do JSON da API oficial da Meta.
    """
    # Remove o sufixo @c.us se existir
    phone_number = sender_id.replace('@c.us', '')
    
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "messages": [{
                        "from": phone_number,
                        "text": {"body": text_body},
                        "type": "text"
                    }]
                }
            }]
        }]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        print(f"Webhook acionado com sucesso: Status {response.status_code}")
    except Exception as e:
        print(f"Erro ao enviar para o webhook: {e}")

def on_message(message):
    sender = message.get('from', 'Desconhecido')
    body = message.get('body', '')
    
    # Ignora mensagens se não tiverem corpo de texto (ex: mídias não suportadas inicialmente)
    if not body:
        return
        
    print(f"Nova mensagem recebida de {sender}: {body}")
    
    # Usa threading puro para não depender do event loop e não travar o WPP_Whatsapp
    import threading
    threading.Thread(target=forward_to_webhook, args=(sender, body)).start()

def start_whatsapp():
    global wa_client
    # Cria a sessão 'UserData' para evitar ler o QR Code toda vez
    wa_client = Create(session="bot_session", catchQR=True, logQR=True)
    wa_client.start()
    
    # Event listener para novas mensagens
    wa_client.onMessage(on_message)
    print("WhatsApp motor iniciado com sucesso.")

def send_message(number: str, text: str):
    if wa_client is None:
        raise Exception("Cliente WhatsApp não está inicializado.")
    
    # number deve ter o sufixo @c.us, a biblioteca geralmente lida ou precisa dele
    if not number.endswith("@c.us"):
        number = f"{number}@c.us"
        
    result = wa_client.sendText(number, text)
    return result
