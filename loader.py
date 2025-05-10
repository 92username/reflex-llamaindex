from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
import os

INDEX_DIR = "index_store"
DOCS_DIR = "docs"

def get_index():
    """Carrega ou cria o índice a partir dos arquivos .md na pasta /docs/."""
    if not os.path.exists(INDEX_DIR):
        print("[loader] Nenhum índice encontrado. Indexando documentos...")
        # Lê os documentos da pasta /docs
        docs = SimpleDirectoryReader(DOCS_DIR).load_data()
        index = VectorStoreIndex.from_documents(docs)
        index.storage_context.persist(persist_dir=INDEX_DIR)
    else:
        print("[loader] Índice existente encontrado. Carregando do disco...")
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        index = load_index_from_storage(storage_context)

    return index
