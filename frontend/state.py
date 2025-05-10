import asyncio
import os
import uuid
import csv
from datetime import datetime

import reflex as rx
from loader import get_index  # carrega o índice com LlamaIndex + GPT-4o-mini

def registrar_interacao(pergunta: str, resposta: str, fonte: str = "chat"):
    """Registra uma interação do usuário (pergunta e resposta) em CSV."""
    os.makedirs('logs', exist_ok=True)
    arquivo_log = 'logs/perguntas.csv'
    arquivo_existe = os.path.isfile(arquivo_log)
    timestamp = datetime.now().isoformat()

    with open(arquivo_log, 'a', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        if not arquivo_existe:
            writer.writerow(['timestamp', 'fonte', 'pergunta', 'resposta'])
        writer.writerow([timestamp, fonte, pergunta, resposta])


class SettingsState(rx.State):
    color: str = "violet"
    font_family: str = "Poppins"


class State(rx.State):
    question: str
    processing: bool = False
    chat_history: list[tuple[str, str]] = []
    user_id: str = str(uuid.uuid4())

    async def answer(self):
        self.processing = True
        yield

        self.chat_history.append((self.question, ""))
        question = self.question
        self.question = ""
        yield

        # ✅ Consulta ao índice contextual com o gpt-4o-mini
        index = get_index()
        query_engine = index.as_query_engine()
        resposta = query_engine.query(question)
        answer = str(resposta)

        # Simula efeito de digitação
        for i in range(len(answer)):
            await asyncio.sleep(0.01)
            self.chat_history[-1] = (
                self.chat_history[-1][0],
                answer[: i + 1],
            )
            yield

        # Finaliza resposta e registra no CSV
        self.chat_history[-1] = (self.chat_history[-1][0], answer)
        registrar_interacao(question, answer)
        self.processing = False
        yield

    async def handle_key_down(self, key: str):
        if key == "Enter":
            async for t in self.answer():
                yield t

    def clear_chat(self):
        self.chat_history = []
        self.processing = False
