"""
LangChain-Hauptagent mit RAG-Fähigkeiten für Bug-Bounty-Planung
"""

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
from langchain.utilities import SerpAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import List, Union, Optional
import re
import os
import json
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

class PenetrationTestAgent:
    """Hauptagent für Bug-Bounty-Planung mit Langchain und RAG"""
    
    def __init__(self, 
                 knowledge_base_path: str = "./knowledge_base",
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.2):
        """
        Initialisiert den Penetrationstest-Agenten
        
        Args:
            knowledge_base_path: Pfad zur Wissensdatenbank mit Dokumenten
            model_name: Name des zu verwendenden LLM-Modells (z.B. gpt-3.5-turbo, gpt-4)
            temperature: Temperatur für den LLM (höher = kreativere Ausgaben)
        """
        self.knowledge_base_path = knowledge_base_path
        self.model_name = model_name
        self.temperature = temperature
        
        # Initialisiere das LLM (Sprachmodell)
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # Setup der verschiedenen Komponenten
        self.vectorstore = self._setup_vectorstore()
        self.tools = self._setup_tools()
        self.agent_executor = self._setup_agent()
    
    def _setup_vectorstore(self):
        """Richtet den Vector Store mit der Wissensdatenbank ein"""
        try:
            # Prüfe, ob der Wissensdatenbankpfad existiert
            if not os.path.exists(self.knowledge_base_path):
                print(f"Warnung: Wissensdatenbankpfad {self.knowledge_base_path} existiert nicht.")
                return None
            
            # Lade Dokumente aus dem Wissensdatenbank-Verzeichnis
            loader = DirectoryLoader(self.knowledge_base_path, glob="**/*.txt", loader_cls=TextLoader)
            documents = loader.load()
            
            if not documents:
                print("Warnung: Keine Dokumente in der Wissensdatenbank gefunden.")
                return None
            
            print(f"Anzahl der geladenen Dokumente aus {self.knowledge_base_path}: {len(documents)}")
            
            # Teile Dokumente in kleinere Chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            # Erstelle Embeddings und Vector Store
            embeddings = OpenAIEmbeddings()
            vectorstore = Chroma.from_documents(texts, embeddings)
            
            return vectorstore
        
        except Exception as e:
            print(f"Fehler beim Einrichten des Vector Stores: {e}")
            return None
    
    def _setup_tools(self):
        """Richtet die Tools für den Agenten ein"""
        tools = []
        
        if self.vectorstore:
            # Tool für den Zugriff auf die Wissensdatenbank
            knowledge_tool = Tool(
                name="Wissensdatenbank",
                func=lambda q: self._query_knowledge_base(q),
                description="Nützlich für Fragen zu Sicherheitsthemen, Pentests und Bug-Bounty-Programmen. Frage nach spezifischen Informationen zur Sicherheit."
            )
            tools.append(knowledge_tool)
        
        return tools
    
    def _setup_agent(self):
        """Richtet den LLM-Agenten ein"""
        # Template für die Agentenanweisung
        template = """
        Du bist ein hochspezialisierter Experte für Cybersicherheit, Penetrationstests und Bug-Bounty-Programme.
        Deine Aufgabe ist es, detaillierte Strategien und Anleitungen für Bug-Bounty-Aufgaben zu entwickeln.
        
        Nutze dein Wissen über Sicherheitsthemen, um hilfreiche Antworten und strukturierte Pläne zu erstellen.
        
        Verfügbare Tools:
        {tools}
        
        Verwende die folgenden Formate für deine Antworten:
        
        Frage: Die Eingabe des Nutzers
        Gedanken: Hier solltest du über den Lösungsansatz nachdenken
        Aktion: Der Name des Tools, das du verwenden möchtest
        Aktions-Eingabe: Die Eingabe für das Tool
        Beobachtung: Das Ergebnis der Aktion
        ... (dieser Gedanken/Aktion/Aktions-Eingabe/Beobachtungs-Prozess kann mehrfach wiederholt werden)
        Gedanken: Jetzt kenne ich die endgültige Antwort
        Finale Antwort: Die strukturierte Antwort auf die ursprüngliche Frage
        
        Beginne!
        
        Frage: {input}
        Gedanken:
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "tools"],
            partial_variables={}
        )
        
        # Ausgabeparser für den Agenten
        class CustomOutputParser(AgentOutputParser):
            def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
                # Prüfe, ob der LLM eine Aktion ausführen möchte
                if "Aktion:" in llm_output:
                    # Extrahiere den Aktionsnamen und die Eingabe
                    action_match = re.search(r"Aktion:\s*(.*?)\nAktions-Eingabe:\s*(.*)", llm_output, re.DOTALL)
                    if action_match:
                        action = action_match.group(1).strip()
                        action_input = action_match.group(2).strip()
                        # Gibt eine Aktion zurück, die vom Agenten-Executor ausgeführt werden soll
                        return AgentAction(tool=action, tool_input=action_input, log=llm_output)
                
                # Prüfe, ob der LLM seine Antwort abgeschlossen hat
                if "Finale Antwort:" in llm_output:
                    final_answer_match = re.search(r"Finale Antwort:\s*(.*)", llm_output, re.DOTALL)
                    if final_answer_match:
                        final_answer = final_answer_match.group(1).strip()
                        # Gibt ein AgentFinish-Objekt zurück, das signalisiert, dass der Agent fertig ist
                        return AgentFinish(
                            return_values={"output": final_answer},
                            log=llm_output,
                        )
                
                # Wenn keine Aktion oder finale Antwort erkannt wurde, setze die Ausgabe als finale Antwort
                return AgentFinish(
                    return_values={"output": llm_output},
                    log=llm_output,
                )
        
        # Erstelle den LLM-Agenten
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=CustomOutputParser(),
            stop=["\nBeobachtung:"],
            allowed_tools=[tool.name for tool in self.tools]
        )
        
        # Erstelle den Agenten-Executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5
        )
        
        return agent_executor
    
    def _query_knowledge_base(self, query: str) -> str:
        """Führt eine Abfrage gegen die Wissensdatenbank durch"""
        if not self.vectorstore:
            return "Die Wissensdatenbank ist nicht verfügbar."
        
        # Durchsuche die Wissensdatenbank
        docs = self.vectorstore.similarity_search(query, k=3)
        
        if not docs:
            return "Keine relevanten Informationen in der Wissensdatenbank gefunden."
        
        # Formatiere die Ergebnisse
        result = "\n\nInformationen aus der Wissensdatenbank:\n"
        for i, doc in enumerate(docs):
            result += f"\n--- Abschnitt {i+1} ---\n"
            result += doc.page_content
            result += f"\n--- Quelle: {os.path.basename(doc.metadata['source'])} ---\n"
        
        return result
    
    def run(self, query: str) -> str:
        """
        Führt eine Anfrage durch den Agenten aus
        
        Args:
            query: Die Anfrage des Benutzers
            
        Returns:
            Die Antwort des Agenten
        """
        if not self.tools:
            # Wenn keine Tools verfügbar sind, verwende das LLM direkt
            response = self.llm.predict(
                f"""Du bist ein Experte für Cybersicherheit, Penetrationstests und Bug-Bounty-Programme.
                Beantworte folgende Frage so detailliert und hilfreich wie möglich:
                
                {query}
                """
            )
            return response
        
        # Führe die Anfrage durch den Agenten-Executor aus
        try:
            response = self.agent_executor.run(query)
            return response
        except Exception as e:
            return f"Fehler bei der Ausführung der Anfrage: {str(e)}"
    
    def add_document_to_knowledge_base(self, content: str, filename: str) -> bool:
        """
        Fügt ein Dokument zur Wissensdatenbank hinzu
        
        Args:
            content: Der Inhalt des Dokuments
            filename: Der Name der Datei, in der der Inhalt gespeichert werden soll
            
        Returns:
            True, wenn das Dokument erfolgreich hinzugefügt wurde, sonst False
        """
        try:
            # Erstelle den Wissensdatenbank-Ordner, falls er nicht existiert
            os.makedirs(self.knowledge_base_path, exist_ok=True)
            
            # Vollständiger Pfad für die neue Datei
            file_path = os.path.join(self.knowledge_base_path, filename)
            
            # Schreibe den Inhalt in die Datei
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Dokument wurde gespeichert unter {file_path}")
            
            # Aktualisiere den Vector Store mit dem neuen Dokument
            self.vectorstore = self._setup_vectorstore()
            
            return True
        
        except Exception as e:
            print(f"Fehler beim Hinzufügen des Dokuments zur Wissensdatenbank: {e}")
            return False 