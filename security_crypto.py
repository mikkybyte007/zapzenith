import os
from cryptography.fernet import Fernet
import base64

# O KMS Master Key idealmente viria de um serviço Vault ou variavel ambiente.
# Para o ZapZenith, exigimos que exista um MASTER_ENCRYPTION_KEY no .env
MASTER_KEY = os.environ.get("MASTER_ENCRYPTION_KEY")

if not MASTER_KEY:
    # Gera uma fallback segura apenas para desenvolvimento, mas avisa o usuário.
    MASTER_KEY = Fernet.generate_key().decode()
    print("WARNING: MASTER_ENCRYPTION_KEY não encontrada no .env. Utilizando chave efêmera. Tokens serão perdidos ao reiniciar.")

def _get_fernet() -> Fernet:
    # Garante padding de 32 bytes em base64 para a chave do fernet
    try:
        return Fernet(MASTER_KEY.encode())
    except ValueError:
        # Tenta sanitizar a chave do usuário se não for base64
        padded = base64.urlsafe_b64encode(MASTER_KEY.encode()[:32].ljust(32, b'\0'))
        return Fernet(padded)

def encrypt_data(plain_text: str) -> str:
    """Criptografa uma string em AES-256 (Fernet)"""
    if not plain_text: return plain_text
    f = _get_fernet()
    encrypted = f.encrypt(plain_text.encode())
    return encrypted.decode()

def decrypt_data(cipher_text: str) -> str:
    """Descriptografa uma string em AES-256 (Fernet)"""
    if not cipher_text: return cipher_text
    f = _get_fernet()
    try:
        decrypted = f.decrypt(cipher_text.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Erro ao descriptografar dados sensíveis: {e}")
        return None
