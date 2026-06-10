import asyncio
from typing import Dict, Any

# Fila assíncrona em memória (Leve, sem necessidade de Redis no MVP)
webhook_queue = asyncio.Queue()

async def process_webhook_queue():
    """Worker que roda em background processando a fila de mensagens"""
    print("Iniciando Background Worker (Queue Processor)...")
    while True:
        try:
            # Pega o próximo webhook da fila
            payload = await webhook_queue.get()
            
            # Aqui acionaremos o motor de IA ou Roteamento do CRM
            await handle_webhook(payload)
            
            # Sinaliza que a tarefa foi concluída
            webhook_queue.task_done()
        except Exception as e:
            print(f"Erro no processamento da fila: {e}")

async def handle_webhook(payload: Dict[str, Any]):
    """Processa individualmente a mensagem fora do tempo da requisição web"""
    from core import handle_incoming_message
    from ai_agent import process_message_with_ai
    
    sender = payload.get("sender")
    body = payload.get("body")
    
    # 1. Salva a mensagem original no banco (via core.py)
    # handle_incoming_message é sincrono, então mandamos rodar no asyncio thread
    await asyncio.to_thread(handle_incoming_message, sender, body)
    
    # 2. Encaminha para o Agente Cognitivo de IA
    await process_message_with_ai(sender, body)

async def enqueue_message(sender: str, body: str):
    """Enfileira a mensagem em tempo O(1) e libera a API"""
    await webhook_queue.put({"sender": sender, "body": body})
    print(f"Mensagem de {sender} adicionada na fila de processamento. (Tamanho atual: {webhook_queue.qsize()})")

def start_queue_worker():
    """Disparado no startup do FastAPI"""
    asyncio.create_task(process_webhook_queue())
