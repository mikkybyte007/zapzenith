# Integração ZapZenith - Instruções para a IA do Lovable

**[User]**: Copie todo o texto abaixo e cole no chat do seu projeto no Lovable (ou v0 / bolt.new) para que ele crie o frontend completo do Painel de Atendimento sincronizado com a nossa nova estrutura.

---

**Contexto para a IA:**
Você é o Lovable, um assistente de desenvolvimento de sistemas. Eu já possuo uma infraestrutura de backend pronta e rodando (Python + FastAPI + Supabase) para um painel de atendimento de WhatsApp chamado "Verthos Zenith". A minha API local cuida da automação do WhatsApp e das gravações no banco.
A sua tarefa é construir EXCLUSIVAMENTE o Frontend (React + TailwindCSS) que irá interagir com o meu banco de dados Supabase e minha API.

**Esquema do Banco de Dados (Já existente no Supabase):**
```sql
-- whatsapp_instances
id (uuid), instance_name (text), whatsapp_number (text), status (text: DISCONNECTED, QRCODE, CONNECTED), qrcode_base64 (text)

-- chats
id (uuid), instance_id (uuid), contact_name (text), contact_number (text), last_message_preview (text), status (text)

-- messages
id (uuid), chat_id (uuid), instance_id (uuid), sender (text: CUSTOMER, ATTENDANT), content (text), created_at (timestamp)
```

**Requisitos e Lógica de Integração:**

1. **Autenticação / Cliente Supabase:** Inicialize o cliente Supabase utilizando as variáveis de ambiente normais (ex: `VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY`). Assuma que vamos monitorar a instância de ID armazenada em `VITE_INSTANCE_ID`.

2. **Tela de Conexão (QR Code):**
   - Consulte a tabela `whatsapp_instances`.
   - Se o status for `QRCODE`, exiba o conteúdo de `qrcode_base64` numa tag `<img>`.
   - Utilize o **Supabase Realtime** para escutar atualizações nesta tabela. Assim que o status mudar para `CONNECTED`, redirecione o usuário automaticamente para o Dashboard de Chats.

3. **Dashboard de Atendimento (Chats e Mensagens):**
   - **Sidebar (Lista de Chats):** Leia a tabela `chats` e liste os contatos. Escute mudanças via Realtime para atualizar o `last_message_preview` instantaneamente.
   - **Área Principal (Mensagens):** Leia as mensagens da tabela `messages` filtrando pelo `chat_id` selecionado. Escute inserções na tabela `messages` via Supabase Realtime para que a tela atualize como um chat ao vivo sem refresh. (Mensagens com `sender: 'CUSTOMER'` ficam na esquerda, `ATTENDANT` na direita).
   - **Envio de Mensagens:** Ao digitar e enviar uma mensagem, o frontend **NÃO** deve fazer um `INSERT` no Supabase. Em vez disso, faça um **POST HTTP** para a minha API Python:
     - **URL:** `VITE_ZAPZENITH_API_URL/send-message` (O padrão local será `http://localhost:8000/send-message`)
     - **Payload:** `{ "number": contact_number, "text": "conteudo da mensagem", "chat_id": "id_do_chat_atual" }`
     - A API retornará `200 OK` e o próprio backend inserirá a mensagem no Supabase (que refletirá na tela via Realtime).

4. **Diretrizes de Design (CRÍTICO):**
   - O painel deve ser visualmente **deslumbrante** e ter uma estética "Premium".
   - Use cores profundas em um tema Dark elegante (ex: Slate 900 de fundo), aplique **Glassmorphism** (painéis semitransparentes com desfoque de fundo) para separar as áreas do chat.
   - Utilize gradientes modernos e vibrantes para detalhes e botões de ação (ex: tons de roxo e azul elétrico).
   - Adicione animações de *hover* e transições suaves ao selecionar contatos ou enviar mensagens.
