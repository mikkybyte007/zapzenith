# ZapZenith - Gateway WhatsApp (Integração Verthos & Lovable)

Este projeto atua como uma ponte (Gateway) entre o sistema **Verthos/Lovable** e o **WhatsApp**, utilizando automações em um navegador headless (Playwright) para se comunicar diretamente como uma instância real do WhatsApp Web via `WPP_Whatsapp`. 

A API foi projetada especificamente com suporte a permissões flexíveis de **CORS** e tipada utilizando os moldes da `OpenAPI`, o que permite fácil acoplamento a plataformas _low-code_ como o **Lovable**.

---

## 🚀 Como Integrar com o Lovable

O Lovable é especialista em consumir APIs REST bem estruturadas. Para que o Lovable se comunique com o seu Gateway local, você deve fornecer a ele a estrutura da sua requisição e expor a API usando o **Ngrok**.

### Passo 1: Informações da Rota
No módulo de APIs do Lovable, você deverá configurar um conector externo apontando para a seguinte rota:

- **Endpoint:** `[SUA_URL_NGROK]/send-message`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`

### Passo 2: Estrutura da Requisição (Body/Payload)
Quando uma ação acontecer no Lovable (ex: disparar uma mensagem no banco de dados Verthos), o Lovable deve enviar um JSON no Body da requisição com este formato:

```json
{
  "number": "5511999999999",
  "text": "Olá! Essa é uma mensagem programada pelo Verthos/Lovable."
}
```

> **Atenção aos números:** O Gateway aceita o número de telefone no formato internacional. Não coloque símbolos (`+`, `-`, ou espaços). Apenas os códigos de país, área e telefone, todos juntos (Ex: `55` `11` `999999999`).

### Passo 3: Configuração Via OpenAPI (Alternativa de Importação)
O projeto conta com o arquivo `openapi.json` incluído na pasta. Se o Lovable solicitar a especificação Swagger/OpenAPI para configurar as rotas magicamente para você, basta carregar ou apontar para esse arquivo. 

---

## 🛠 Como Rodar a API Localmente

Para começar a enviar arquivos, você precisa ligar o Gateway no seu computador e parear com seu WhatsApp.

1. **Ative o ambiente e instale as dependências**
   Recomendamos usar Python 3.10 ou superior.
   ```shell
   # Criação do ambiente virtual
   python -m venv venv
   
   # Ativação (Windows)
   .\venv\Scripts\activate
   
   # Instalar Dependências e Browsers
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Inicie a Aplicação**
   No seu terminal, inicie o servidor:
   ```shell
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```
   *Um QR Code aparecerá no seu terminal. Escaneie-o com seu celular (Aparelhos Conectados).*

3. **Exponha a porta para o Lovable ler (Via Ngrok)**
   Em uma segunda janela de terminal, digite:
   ```shell
   ngrok http 8000
   ```
   *Pegue a URL HTTPs gerada pelo ngrok, insira-a no campo "Base URL" do Lovable, e você estará comunicando a Nuvem com o seu PC!* 

---

## 🧩 Estrutura do Projeto
- `core.py`: Mantém o estado ativo do "Motor" gerenciador de eventos do Playwright e WhatsApp.
- `api.py`: Framework e roteamento web do FastAPI e definições de tipagem Pydantic.
- `utils.py`: Auxiliares de engenharia social, como simulação aleatória de tempo de digitação humana, minimizando risco de shadow-ban no WhatsApp.
