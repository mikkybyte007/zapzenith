# Integração ZapZenith - Instruções para a IA do Lovable

**[User]**: Copie todo o texto abaixo a partir de "Contexto para a IA" e cole no chat do seu projeto no Lovable para que ele crie a integração automaticamente para você.

---

**Contexto para a IA:**
Você é o Lovable, e eu estou integrando uma API Customizada de disparo de mensagens do WhatsApp chamada "ZapZenith" ao meu sistema. Essa API substitui a API Oficial da Meta para evitar custos. Minha infraestrutura já está pronta e rodando, e precisamos configurar as ações aqui no frontend/backend para se comunicar com ela via HTTP padrão.

**Especificação da API ZapZenith:**
- **URL Base:** A API está hospedada externamente e eu vou inserir a URL base dinamicamente. Por favor, crie uma variável de ambiente ou um campo de configuração no app chamado `VITE_ZAPZENITH_API_URL` (ou equivalente no Supabase Secrets `ZAPZENITH_API_URL`) para armazenar o link do Ngrok (Ex: `https://abcd.ngrok-free.app`).
- **Endpoint:** `POST` na rota `/send-message`.
- **Headers Requeridos:** `Content-Type: application/json`.
- **Body Esperado:** O corpo da requisição é um JSON contendo `number` (string) e `text` (string). O número de telefone deve usar formato internacional limpo (ex: `5511999999999`).
- **Resposta da API:** Retorna HTTP 200 `{ "status": "sent", "response": { ... } }` em caso de sucesso, ou HTTP 500 `{ "detail": "error message" }` em caso de erro.
- **CORS:** O Gateway já está com CORS totalmente habilitado (allow origin `*`), portanto chamadas client-side via `fetch` do browser funcionarão normalmente sem bloqueio.

**Suas Tarefas (Lovable):**
1. Crie uma abstração ou serviço em TypeScript/JavaScript responsável por fazer o disparo das mensagens. Se o nosso projeto tiver Supabase configurado, crie preferencialmente uma Edge Function chamada `send-whatsapp` para mascarar a URL da API externa e proteger as requisições. Se for puro frontend, faça via `fetch` isolado.
2. Implemente uma função reutilizável onde possamos passar apenas o número de destino e o texto.
3. Ajuste os fluxos do meu sistema (onde era esperado usar a API oficial da Meta) para acionar esta nova ação/serviço customizado ao invez de usar a integração oficial.
4. Me avise onde eu devo configurar no painel os Secrets (se usar Supabase) ou as variáveis de ambiente (se usar Vite) para colar a minha URL pública gerada pelo Ngrok.
