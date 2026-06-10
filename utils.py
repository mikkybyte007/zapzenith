import asyncio
import random

async def human_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """
    Simula o delay de um humano digitando ou realizando uma ação.
    """
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)

async def typing_delay(text: str):
    """
    Simula o tempo de digitação baseado no tamanho do texto.
    Aproximadamente 5 caracteres por segundo (0.2s por char) + um pouco de variância.
    """
    base_time = len(text) * 0.1
    delay = random.uniform(base_time, base_time * 1.5)
    await asyncio.sleep(delay)
