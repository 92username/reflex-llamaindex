import os
from dotenv import load_dotenv
load_dotenv()

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI

INDEX_DIR = "index_store"
DOCS_DIR = "docs"

def get_index():
    """
    Cria ou carrega um índice com base nos arquivos Markdown da pasta /docs,
    usando o modelo GPT-4o-mini via API da OpenAI.
    """
    # Define o LLM que será usado nas queries
    llm = OpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        system_prompt=(
    "Você é um assistente técnico simpático e prestativo, que responde com clareza, "
    "mas também com empatia. Use uma linguagem natural, como se estivesse conversando com um humano. "
    "Evite parecer um robô ou responder de forma seca.\n\n"
    "Baseie suas respostas somente na documentação fornecida.\n"
    "Responda sempre em Português (Brasil), mesmo que a pergunta esteja em outro idioma.\n"
    "Se não souber a resposta, diga que não sabe ou informe que a informação não está disponível."
)

    )

    if not os.path.exists(INDEX_DIR):
        print("[loader] Nenhum índice encontrado. Indexando documentos...")
        documents = SimpleDirectoryReader(DOCS_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents, llm=llm)
        index.storage_context.persist(persist_dir=INDEX_DIR)
    else:
        print("[loader] Índice existente encontrado. Carregando...")
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        index = load_index_from_storage(storage_context)

    return index
