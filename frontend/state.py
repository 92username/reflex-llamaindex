import asyncio
import json
import os
import uuid
import csv
from datetime import datetime

import httpx
import reflex as rx
from openai import AsyncOpenAI


def registrar_interacao(pergunta: str, resposta: str, fonte: str = "chat"):
    """
    Registra uma interação do usuário (pergunta e resposta) em um arquivo CSV.
    
    Args:
        pergunta: A pergunta feita pelo usuário
        resposta: A resposta gerada pela IA
        fonte: A fonte da interação (padrão: "chat")
    """
    # Criar a pasta logs/ se ela não existir
    os.makedirs('logs', exist_ok=True)
    
    # Caminho para o arquivo CSV
    arquivo_log = 'logs/perguntas.csv'
    
    # Verificar se o arquivo já existe para decidir se inclui o cabeçalho
    arquivo_existe = os.path.isfile(arquivo_log)
    
    # Obter timestamp atual em formato ISO
    timestamp = datetime.now().isoformat()
    
    # Abrir o arquivo em modo de adição
    with open(arquivo_log, 'a', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        
        # Escrever cabeçalho se o arquivo for novo
        if not arquivo_existe:
            writer.writerow(['timestamp', 'fonte', 'pergunta', 'resposta'])
        
        # Escrever a linha com os dados da interação
        writer.writerow([timestamp, fonte, pergunta, resposta])


class SettingsState(rx.State):
    # The accent color for the app
    color: str = "violet"

    # The font family for the app
    font_family: str = "Poppins"


class State(rx.State):
    # The current question being asked.
    question: str

    # Whether the app is processing a question.
    processing: bool = False

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = []

    user_id: str = str(uuid.uuid4())

    async def answer(self):
        # Set the processing state to True.
        self.processing = True
        yield

        # convert chat history to a list of dictionaries
        chat_history_dicts = []
        for chat_history_tuple in self.chat_history:
            chat_history_dicts.append(
                {"role": "user", "content": chat_history_tuple[0]}
            )
            chat_history_dicts.append(
                {"role": "assistant", "content": chat_history_tuple[1]}
            )

        self.chat_history.append((self.question, ""))

        # Clear the question input.
        question = self.question
        self.question = ""

        # Yield here to clear the frontend input before continuing.
        yield

        # Inicializar o cliente da OpenAI com API key
        # A API key será obtida da variável de ambiente OPENAI_API_KEY
        client = AsyncOpenAI()
        
        # Preparar a lista de mensagens para a API da OpenAI
        messages = [
            {"role": "system", "content": "Você é um assistente prestativo e amigável."}
        ]
        
        # Adicionar histórico de conversa
        for msg in chat_history_dicts:
            messages.append(msg)
            
        # Adicionar a pergunta atual
        messages.append({"role": "user", "content": question})
        
        # Chamar a API da OpenAI com streaming
        stream = await client.chat.completions.create(
            model="gpt-4.1-nano",  # ou outro modelo de sua preferência
            messages=messages,
            stream=True,
        )

        # Add to the answer as the chatbot responds.
        answer = ""
        yield

        # Processar resposta em streaming
        async for chunk in stream:
            if hasattr(chunk.choices[0].delta, "content"):
                if chunk.choices[0].delta.content is None:
                    break
                answer += chunk.choices[0].delta.content
                self.chat_history[-1] = (self.chat_history[-1][0], answer)
                yield

        # Ensure the final answer is added to chat history
        if answer:
            self.chat_history[-1] = (self.chat_history[-1][0], answer)
            yield

        # Set the processing state to False.
        self.processing = False
        
        # Registrar a interação no CSV
        resposta_final = self.chat_history[-1][1]
        registrar_interacao(question, resposta_final)

    async def handle_key_down(self, key: str):
        if key == "Enter":
            async for t in self.answer():
                yield t

    def clear_chat(self):
        # Reset the chat history and processing state
        self.chat_history = []
        self.processing = False
