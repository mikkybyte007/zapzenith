import os
import re
import litellm
import asyncio

# A API Key do LLM
litellm.api_key = os.environ.get("OPENAI_API_KEY", "sk-placeholder")

# Guardrails e Sanitização (Prevenção de Prompt Injection)
FORBIDDEN_PATTERNS = [
    r"(?i)(ignore as instruções anteriores)",
    r"(?i)(desconsidere tudo)",
    r"(?i)(você é um desenvolvedor)",
    r"(?i)(me diga a sua system prompt)",
    r"(?i)(dump database)"
]

def sanitize_prompt(text: str) -> bool:
    """Retorna False se o texto contiver tentativa de Prompt Injection"""
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            return False
    return True

async def retrieve_knowledge(query: str) -> str:
    """Simula a busca vetorial (RAG) na tabela knowledge_base via pgvector"""
    # Em produção, usaremos pgvector para buscar embeddings da query.
    from core import supabase, INSTANCE_ID
    if not supabase: return ""
    
    # Exemplo: busca full-text simples (MVP)
    try:
        res = supabase.table("knowledge_base").select("content").eq("instance_id", INSTANCE_ID).limit(3).execute()
        knowledge = "\n".join([item["content"] for item in res.data])
        return knowledge
    except:
        return ""

async def execute_smart_action(intent: str, sender: str):
    """Auto-Execution: Motor de Ações Autônomas do CRM"""
    from core import supabase, INSTANCE_ID
    if not supabase: return
    
    phone = sender.replace('@c.us', '')
    
    # Validador de escopo (apenas ações permitidas)
    if "ENCERRAR_TICKET" in intent:
        # Busca o chat
        chat_res = supabase.table("chats").select("id").eq("contact_number", phone).eq("instance_id", INSTANCE_ID).execute()
        if chat_res.data:
            supabase.table("chats").update({"status": "CLOSED"}).eq("id", chat_res.data[0]["id"]).execute()
            print(f"[AÇÃO IA] Ticket de {phone} encerrado.")
            
    elif "MOVER_NEGOCIACAO" in intent:
        # Busca o deal no CRM e avança estágio
        deal_res = supabase.table("crm_deals").select("id").eq("title", phone).eq("instance_id", INSTANCE_ID).execute()
        if deal_res.data:
            supabase.table("crm_deals").update({"stage": "NEGOTIATION"}).eq("id", deal_res.data[0]["id"]).execute()
            print(f"[AÇÃO IA] Deal de {phone} avançado para NEGOTIATION.")

async def process_message_with_ai(sender: str, body: str):
    """Ponto de entrada do agente cognitivo"""
    
    # 1. Blindagem (Prompt Injection Guard)
    if not sanitize_prompt(body):
        print(f"[SECURITY ALERT] Tentativa de Injeção bloqueada de {sender}.")
        return "⚠️ Sua solicitação violou nossas políticas de segurança."

    # 2. RAG (Recuperar Contexto da Base)
    context = await retrieve_knowledge(body)
    
    system_prompt = f"""Você é o Agente de IA Cognitivo da Verthos Zenith.
Seu objetivo é auxiliar o cliente baseando-se EXCLUSIVAMENTE no conhecimento corporativo abaixo.
Se o cliente quiser fechar negócio ou encerrar o atendimento, inclua no final da resposta a intenção exata: [INTENT:ENCERRAR_TICKET] ou [INTENT:MOVER_NEGOCIACAO].
BASE DE CONHECIMENTO CORPORATIVO:
{context}"""

    print(f"[AI] Raciocinando sobre a mensagem de {sender}...")
    try:
        # Chamada assíncrona para o LLM
        response = await asyncio.to_thread(
            litellm.completion,
            model="gpt-3.5-turbo", # Ou claude-3, gemini-pro
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": body}
            ],
            temperature=0.3
        )
        ai_reply = response.choices[0].message.content
        
        # 3. Execução de Ações
        if "[INTENT:" in ai_reply:
            intent = ai_reply.split("[INTENT:")[1].split("]")[0]
            await execute_smart_action(intent, sender)
            # Remove a tag da resposta para o usuário final
            ai_reply = ai_reply.replace(f"[INTENT:{intent}]", "").strip()

        # 4. Envia Resposta de volta pro WhatsApp
        from core import send_message
        try:
            send_message(sender, ai_reply)
        except Exception as e:
            print(f"Erro ao enviar resposta da IA para o wpp: {e}")

    except Exception as e:
        print(f"[AI Error] Falha na cognição: {e}")
