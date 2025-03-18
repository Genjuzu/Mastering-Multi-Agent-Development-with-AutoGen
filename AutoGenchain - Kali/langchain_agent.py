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
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

class PenetrationTestAgent:
    """Hauptagent für Bug-Bounty-Planung mit Langchain und RAG"""
    
    def __init__(self, 
                 knowledge_base_path: str = "./bugbounty-agents/knowledge_base",
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.2):
        """
        Initialisiert den Penetration Test Agenten
        
        Args:
            knowledge_base_path: Pfad zur Wissensdatenbank
            model_name: Name des zu verwendenden LLM-Modells
            temperature: Temperatur für das LLM
        """
        self.knowledge_base_path = knowledge_base_path
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model_name=model_name, 
            temperature=temperature,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # Speicher für Konversationen
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Vektorstore für RAG einrichten
        self.vectorstore = self._setup_vectorstore()
        
        # Tools einrichten
        self.tools = self._setup_tools()
        
        # Agent einrichten
        self.agent_chain = self._setup_agent()
    
    def _setup_vectorstore(self):
        """Richtet den Vektorstore für RAG ein"""
        # Prüfe, ob die Wissensdatenbank existiert
        if not os.path.exists(self.knowledge_base_path):
            os.makedirs(self.knowledge_base_path)
            print(f"Wissensdatenbank-Verzeichnis erstellt unter {self.knowledge_base_path}")
            print("Füge bitte Dokumente zum Wissensdatenbank-Verzeichnis hinzu.")
            return None
        
        try:
            # Versuche, vorhandene Dokumente zu laden
            loader = DirectoryLoader(self.knowledge_base_path, glob="**/*.txt", loader_cls=TextLoader)
            documents = loader.load()
            
            if not documents:
                print("Keine Dokumente in der Wissensdatenbank gefunden.")
                return None
            
            # Teile Dokumente in kleinere Chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            # Erstelle Embeddings und Vektordatenbank
            embeddings = OpenAIEmbeddings()
            vectorstore = Chroma.from_documents(texts, embeddings)
            print(f"Vektorstore mit {len(texts)} Textchunks erstellt.")
            
            return vectorstore
        except Exception as e:
            print(f"Fehler beim Einrichten des Vektorstores: {e}")
            return None
    
    def _setup_tools(self):
        """Richtet die Tools für den Agenten ein"""
        tools = []
        
        # Wissensdatenbank-Abfragetool
        if self.vectorstore:
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            knowledge_base_tool = Tool(
                name="PenetrationTestKnowledge",
                func=retriever.get_relevant_documents,
                description="Nützlich für Fragen über Penetrationstests, Schwachstellen und Hacking-Techniken. Die Eingabe sollte eine Frage sein, die sich auf das Thema bezieht."
            )
            tools.append(knowledge_base_tool)
        
        # TODO: Weitere Tools für spezifische Penetrationstest-Aufgaben hinzufügen
        
        return tools
    
    def _setup_agent(self):
        """Richtet den Langchain-Agenten ein"""
        # Prompt-Template für den Agenten
        template = """Du bist ein Experte für Penetrationstests und Bug-Bounty-Jagd. 
        Du hast Zugriff auf eine Wissensdatenbank mit Informationen zu Penetrationstests und Schwachstellen.
        
        Verwende die folgenden Tools, um den Benutzer bei der Planung von Bug-Bounty-Aktivitäten zu unterstützen:
        {tools}
        
        Führe eine gründliche Analyse durch und erkläre deine Überlegungen, bevor du eine endgültige Antwort gibst.
        
        Bisheriger Konversationsverlauf:
        {chat_history}
        
        Aktuelle Aufgabe: {input}
        
        Denke Schritt für Schritt:
        {agent_scratchpad}
        """
        
        prompt = PromptTemplate(
            input_variables=["input", "chat_history", "agent_scratchpad", "tools"],
            template=template
        )
        
        # Parser für Agentenausgabe
        class CustomOutputParser(AgentOutputParser):
            def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
                # Prüfe, ob der LLM eine Aktion ausführen möchte
                action_match = re.search(r"Action: (.*?)\nAction Input: (.*)", llm_output, re.DOTALL)
                if action_match:
                    action = action_match.group(1).strip()
                    action_input = action_match.group(2).strip()
                    return AgentAction(tool=action, tool_input=action_input, log=llm_output)
                
                # Wenn keine Aktion angegeben ist, betrachte es als finale Antwort
                return AgentFinish(
                    return_values={"output": llm_output.strip()},
                    log=llm_output,
                )
        
        output_parser = CustomOutputParser()
        
        # LLM Chain
        llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )
        
        # Tool-Namen für den Agenten verfügbar machen
        tool_names = [tool.name for tool in self.tools]
        
        # Agent
        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["\nObservation:"],
            allowed_tools=tool_names
        )
        
        # Agent Executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def run(self, query: str) -> str:
        """
        Führt eine Anfrage mit dem Agenten aus
        
        Args:
            query: Die Benutzereingabe/Anfrage
        
        Returns:
            Die Antwort des Agenten
        """
        if not self.tools:
            return "Der Agent hat keine Tools zur Verfügung. Bitte stelle sicher, dass die Wissensdatenbank korrekt eingerichtet ist."
        
        try:
            result = self.agent_chain.run(input=query)
            return result
        except Exception as e:
            return f"Fehler bei der Ausführung der Anfrage: {e}"
    
    def add_document_to_knowledge_base(self, content: str, filename: str) -> bool:
        """
        Fügt ein Dokument zur Wissensdatenbank hinzu
        
        Args:
            content: Der Inhalt des Dokuments
            filename: Der Dateiname für das Dokument
            
        Returns:
            True, wenn erfolgreich hinzugefügt, sonst False
        """
        try:
            if not os.path.exists(self.knowledge_base_path):
                os.makedirs(self.knowledge_base_path)
            
            file_path = os.path.join(self.knowledge_base_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Vektorstore neu einrichten
            self.vectorstore = self._setup_vectorstore()
            
            # Tools aktualisieren
            self.tools = self._setup_tools()
            
            # Agent neu einrichten
            self.agent_chain = self._setup_agent()
            
            return True
        except Exception as e:
            print(f"Fehler beim Hinzufügen des Dokuments: {e}")
            return False


# Beispielverwendung
if __name__ == "__main__":
    agent = PenetrationTestAgent()
    
    # Füge ein Beispieldokument hinzu, falls die Wissensdatenbank leer ist
    if not agent.vectorstore:
        example_content = """
        Grundlegende Phasen eines Penetrationstests:
        
        1. Aufklärung (Reconnaissance): Sammlung von Informationen über das Zielsystem
           - Passive Aufklärung: OSINT, Whois-Lookup, DNS-Informationen
           - Aktive Aufklärung: Port Scanning, Diensterkennung
        
        2. Schwachstellenanalyse (Vulnerability Assessment):
           - Identifizierung potenzieller Schwachstellen
           - Priorisierung basierend auf Risiko und Auswirkung
        
        3. Exploitation:
           - Ausnutzung identifizierter Schwachstellen
           - Erstellung von Proof-of-Concept-Exploits
        
        4. Post-Exploitation:
           - Privilege Escalation
           - Laterale Bewegung im Netzwerk
           - Persistenzmechanismen
        
        5. Berichterstattung:
           - Dokumentation gefundener Schwachstellen
           - Empfehlungen zur Behebung
           - Risikobewertung
        """
        agent.add_document_to_knowledge_base(example_content, "pentest_basics.txt")
        
        # Agent neu initialisieren
        agent = PenetrationTestAgent()
    
    # Testeingabe
    result = agent.run("Wie kann ich bei einem Bug-Bounty-Programm mit der Aufklärungsphase beginnen?")
    print(result) 