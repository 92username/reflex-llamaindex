import os
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
        temperature=0.2
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
