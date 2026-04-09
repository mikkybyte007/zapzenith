from WPP_Whatsapp import Create
import asyncio

# A instância global do client/wa será armazenada aqui
wa_client = None

def on_message(message):
    print(f"Nova mensagem de {message.get('from', 'Desconhecido')}: {message.get('body', '')}")

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
