import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Cargar las variables de entorno (necesario para la API Key de OpenAI)
load_dotenv()

# Constantes
KNOWLEDGE_BASE_DIR = "data/knowledge_base"
VECTOR_STORE_DIR = "data/chroma_db"

class RAGManager:
    """
    Gestiona la creación y carga de la base de conocimientos vectorial.
    """
    def __init__(self):
        self.embeddings_model = OpenAIEmbeddings()
        self.vector_store = None

    def _load_documents(self):
        """Carga los documentos desde el directorio especificado."""
        print(f"Cargando documentos desde '{KNOWLEDGE_BASE_DIR}'...")
        # Usamos un TextLoader para cada archivo para evitar problemas con metadatos
        loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        return loader.load()

    def _split_documents(self, documents):
        """Divide los documentos en chunks más pequeños."""
        print("Dividiendo documentos en chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Tamaño del chunk en caracteres
            chunk_overlap=200, # Solapamiento entre chunks
            length_function=len
        )
        return text_splitter.split_documents(documents)

    def create_and_save_vector_store(self):
        """
        Crea la base de datos de vectores a partir de los documentos
        y la guarda de forma persistente con ChromaDB.
        """
        documents = self._load_documents()
        if not documents:
            print("No se encontraron documentos para procesar.")
            return

        chunks = self._split_documents(documents)
        
        print("Creando y guardando el vector store con ChromaDB...")
        # Chroma se encarga de la persistencia si le pasamos un directorio
        self.vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=self.embeddings_model,
            persist_directory=VECTOR_STORE_DIR
        )
        print(f"Vector store guardado en '{VECTOR_STORE_DIR}'.")

    def load_vector_store(self):
        """
        Carga la base de datos de vectores persistente de ChromaDB.
        Retorna True si se cargó correctamente, False en caso contrario.
        """
        if not os.path.exists(VECTOR_STORE_DIR):
            print(f"El directorio del vector store '{VECTOR_STORE_DIR}' no existe.")
            return False
        
        print(f"Cargando vector store desde '{VECTOR_STORE_DIR}'...")
        self.vector_store = Chroma(
            persist_directory=VECTOR_STORE_DIR, 
            embedding_function=self.embeddings_model
        )
        print("Vector store cargado.")
        return True

    def reload_vector_store(self):
        """Recarga el vector store desde el disco. Devuelve True si fue exitoso."""
        logging.info("Recargando el vector store desde el disco...")
        return self.load_vector_store()

    def get_retriever(self):
        """Devuelve un retriever para realizar búsquedas."""
        if self.vector_store is None:
            raise ValueError("El vector store no ha sido cargado. Ejecuta load_vector_store() primero.")
        # as_retriever() convierte nuestra base de datos en un objeto que LangChain puede usar para buscar
        return self.vector_store.as_retriever(search_kwargs={"k": 3}) # k=3 -> devuelve los 3 chunks más relevantes

# --- Bloque para ejecución directa (para crear el índice por primera vez) ---
if __name__ == "__main__":
    print("Ejecutando el gestor de RAG para crear el índice inicial...")
    
    # NOTA: Asegúrate de tener un archivo .env con tu OPENAI_API_KEY
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: La variable de entorno OPENAI_API_KEY no está configurada.")
        print("Por favor, crea un archivo .env y añade tu clave de API de OpenAI.")
    else:
        manager = RAGManager()
        manager.create_and_save_vector_store()
