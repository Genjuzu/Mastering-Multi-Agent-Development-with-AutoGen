"""
Test der Wissensdatenbank-Integration für den Langchain-Agenten
"""

import os
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Lade Umgebungsvariablen
load_dotenv()

# Prüfe, ob der OpenAI API-Schlüssel gesetzt ist
if not os.getenv("OPENAI_API_KEY"):
    print("FEHLER: OPENAI_API_KEY Umgebungsvariable ist nicht gesetzt.")
    print("Bitte erstellen Sie eine .env-Datei mit Ihrem API-Schlüssel.")
    exit(1)

def initialize_vector_store(knowledge_base_path):
    """Initialisiert den Vector Store mit der Wissensdatenbank"""
    print(f"Initialisiere Vector Store mit Dokumenten aus: {knowledge_base_path}")
    
    # Lade Dokumente aus dem Wissensdatenbank-Verzeichnis
    loader = DirectoryLoader(knowledge_base_path, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    print(f"Anzahl der geladenen Dokumente: {len(documents)}")
    for doc in documents:
        print(f"- {os.path.basename(doc.metadata['source'])}")
    
    # Teile Dokumente in kleinere Chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print(f"Dokumente in {len(texts)} Chunks aufgeteilt")
    
    # Erstelle Embeddings und Vector Store
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(texts, embeddings)
    print("Vector Store erfolgreich erstellt")
    
    return vector_store

def test_query(vector_store, query):
    """Testet eine Abfrage gegen den Vector Store"""
    print(f"\n--- Teste Abfrage: '{query}' ---")
    
    # Erstelle einen Retriever aus dem Vector Store
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Hole relevante Dokumente für die Abfrage
    docs = retriever.get_relevant_documents(query)
    
    print(f"Anzahl der zurückgegebenen Dokumente: {len(docs)}")
    
    # Zeige gefundene Dokumente
    for i, doc in enumerate(docs):
        print(f"\nDokument {i+1}:")
        print(f"Quelle: {os.path.basename(doc.metadata['source'])}")
        print(f"Inhalt: {doc.page_content[:300]}...")
    
    # Erstelle einen QA-Chain mit dem Retriever und einem LLM
    llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        verbose=True
    )
    
    # Führe die Abfrage durch
    print("\nAntwort des RAG-Systems:")
    result = qa_chain.run(query)
    print(result)
    
    return result

def main():
    """Hauptfunktion"""
    knowledge_base_path = "./bugbounty-agents/knowledge_base"
    
    print("=== Test der Bug-Bounty-Wissensdatenbank ===\n")
    
    # Initialisiere den Vector Store
    vector_store = initialize_vector_store(knowledge_base_path)
    
    # Teste verschiedene Abfragen
    test_queries = [
        "Was sind die OWASP Top 10 und welche Schwachstellen gehören dazu?",
        "Wie läuft die Aufklärungsphase bei einem Penetrationstest ab?",
        "Welche Maßnahmen zur Prävention von SQL-Injection gibt es?",
        "Wie funktionieren Bug-Bounty-Programme und welche Arten gibt es?",
        "Was sind typische Beispiel-Payloads für XSS-Angriffe?",
        "Wie kann ich meine API gegen SSRF-Angriffe schützen?"
    ]
    
    for query in test_queries:
        test_query(vector_store, query)
        print("\n" + "="*50 + "\n")
    
    # Interaktiver Modus für benutzerdefinierte Abfragen
    print("\n=== Interaktiver Modus ===")
    print("Geben Sie Ihre Fragen ein (oder 'exit' zum Beenden):")
    
    while True:
        user_query = input("\nIhre Frage: ")
        if user_query.lower() in ['exit', 'quit', 'q']:
            break
        
        test_query(vector_store, user_query)

if __name__ == "__main__":
    main() 