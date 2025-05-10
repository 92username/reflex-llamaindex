from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
"""
This module provides functionality to load or create a vector index from markdown documents.

The index is used for efficient document retrieval and search operations. If an existing
index is found in the specified directory, it loads the index from storage. Otherwise,
it creates a new index by reading markdown files from the docs directory.

Constants:
    INDEX_DIR (str): Directory path where the index is stored.
    DOCS_DIR (str): Directory path where markdown documents are located.

Functions:
    get_index(): Loads an existing index or creates a new one from markdown documents.
"""
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
