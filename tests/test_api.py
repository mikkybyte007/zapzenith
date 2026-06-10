import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adiciona o diretório raiz ao sys.path para importar api
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "ZapZenith" in response.json()["status"]

def test_send_message_validation_error():
    # Envio de Payload malicioso/inválido (SQLi/XSS prevention on Phone Number)
    payload = {
        "number": "5511999999999<script>",
        "text": "Teste"
    }
    response = client.post("/send-message", json=payload)
    # Pydantic deve barrar (422 Unprocessable Entity)
    assert response.status_code == 422

def test_send_message_buffer_overflow_prevention():
    # Envio de Payload imenso
    payload = {
        "number": "5511999999999",
        "text": "A" * 5000
    }
    response = client.post("/send-message", json=payload)
    # Pydantic deve barrar pelo max_length=4096 (422)
    assert response.status_code == 422

def test_rate_limiting_flood():
    # Dispara múltiplas requisições para a rota protegida
    for _ in range(6):
        client.post("/start-session")
        
    # A última requisição (limite = 5/min) deve retornar 429 Too Many Requests
    response = client.post("/start-session")
    assert response.status_code == 429
