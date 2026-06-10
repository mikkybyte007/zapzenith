# Integração ZapZenith (Motor DKW System) - Instruções para a IA do Lovable

**[User]**: Copie todo o texto abaixo e cole no chat do seu projeto no Lovable (ou v0 / bolt.new) para que ele crie o frontend completo do Painel de Atendimento sincronizado com a nossa nova arquitetura Sênior DKW.

---

**Contexto para a IA:**
Você é o Lovable, um assistente de desenvolvimento de sistemas. Eu possuo um backend de nível Enterprise (Python + FastAPI + Supabase) rodando localmente para um painel corporativo chamado "Verthos Zenith". A minha API local cuida do motor de Inteligência Artificial Cognitivo (RAG), automação Multicanal do WhatsApp, criptografia AES-256 e das gravações seguras no banco.

A sua tarefa é construir EXCLUSIVAMENTE o Frontend (React/Vite + TypeScript + TailwindCSS) que irá interagir com meu Supabase e com a minha API. O frontend não possui lógicas de IA pesadas; ele é apenas o cliente visual (CRM e Chats).

**Esquema do Banco de Dados (Já existente no Supabase):**
```sql
-- whatsapp_instances
id (uuid), instance_name (text), whatsapp_number (text), status (text: DISCONNECTED, QRCODE, CONNECTED), qrcode_base64 (text)

-- chats
id (uuid), instance_id (uuid), contact_name (text), contact_number (text), last_message_preview (text), status (text: PENDING, OPEN, CLOSED)

-- messages
id (uuid), chat_id (uuid), instance_id (uuid), sender (text: CUSTOMER, ATTENDANT, SYSTEM), content (text), created_at (timestamp)

-- crm_deals (NOVO: PIPELINE KANBAN)
id (uuid), instance_id (uuid), chat_id (uuid), title (text), value (numeric), stage (text: LEAD, MEETING, NEGOTIATION, WON, LOST)

-- knowledge_base (NOVO: BASE DE CONHECIMENTO RAG)
id (uuid), instance_id (uuid), content (text), embedding (vector)
```

**Requisitos e Componentes Visuais (DKW System Pattern):**

1. **Dashboard Multicanal e CRM Dinâmico (Kanban):**
   - O layout deve possuir uma navegação lateral alternando entre "Caixa de Entrada (Chats)", "CRM (Kanban)" e "Base de Conhecimento (IA)".
   - **CRM Kanban:** Construa um board arrastar-e-soltar (Drag and Drop) lendo a tabela `crm_deals`. As colunas são os estágios (LEAD, MEETING, NEGOTIATION, WON, LOST). Ao soltar um card, faça um `UPDATE` no Supabase alterando a coluna `stage`. (O backend processará as automações via webhooks do banco).

2. **Base de Conhecimento (Gerenciamento do RAG):**
   - Crie uma tela simples para o usuário gerenciar a tabela `knowledge_base`.
   - Inclua um formulário/textarea para o usuário digitar instruções corporativas e um botão "Salvar". Isso fará um `INSERT` na tabela `knowledge_base` (apenas o campo `content`, o backend cuidará dos embeddings vetoriais de IA depois).

3. **Caixa de Entrada (Chats ao vivo com IA):**
   - **Sidebar (Lista de Chats):** Leia a tabela `chats` e filtre pelo `instance_id`.
   - **Área Principal:** Exiba as mensagens da tabela `messages` em tempo real (Supabase Realtime). Mensagens com sender 'SYSTEM' ou 'ATTENDANT' ficam na direita, 'CUSTOMER' na esquerda.
   - **Botão "Desativar IA":** Um botão no cabeçalho do chat que permite ao humano assumir o controle (apenas visual por enquanto, mock de status).
   - Ao digitar e enviar uma mensagem, faça um **POST HTTP** com Axios (ou Fetch com Exponential Backoff) para a API:
     - `URL`: `VITE_ZAPZENITH_API_URL/send-message`
     - `Payload`: `{ "number": contact_number, "text": "conteudo da mensagem", "chat_id": "id_do_chat_atual" }`

4. **Diretrizes de Design e UX (CRÍTICO):**
   - Estética **Enterprise / Premium Dark**.
   - Use o esquema de cores Slate 950 com acentos de Aurora (Violeta/Azul Elétrico).
   - **Glassmorphism:** Use painéis translúcidos (`backdrop-blur-xl`, `bg-white/5`, bordas de vidro `border-white/10`).
   - Implemente Skeleton Loaders requintados e framer-motion (se possível) ou CSS transitions suaves ao mover cards no Kanban.
   - O projeto deve ser impecável. Use React puro e bibliotecas sólidas. Não crie componentes vulneráveis a XSS (sempre renderize mensagens como texto literal).
