"""
Integration zwischen Langchain und AutoGen Agenten für Bug-Bounty-Planung
"""

import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Importiere unsere benutzerdefinierten Module
from langchain_agent import PenetrationTestAgent
from autogen_agents import BugBountyAgents

# Lade Umgebungsvariablen
load_dotenv()

class HybridAgentManager:
    """Manager für die Integration von Langchain und AutoGen Agenten"""
    
    def __init__(self,
                knowledge_base_path: str = "./bugbounty-agents/knowledge_base",
                langchain_model: str = "gpt-3.5-turbo",
                autogen_model: str = "gpt-3.5-turbo",
                langchain_temperature: float = 0.2,
                autogen_temperature: float = 0.7):
        """
        Initialisiert den Hybrid-Agent-Manager
        
        Args:
            knowledge_base_path: Pfad zur Wissensdatenbank
            langchain_model: Name des für Langchain zu verwendenden LLM-Modells
            autogen_model: Name des für AutoGen zu verwendenden LLM-Modells
            langchain_temperature: Temperatur für den Langchain-Agenten
            autogen_temperature: Temperatur für die AutoGen-Agenten
        """
        self.knowledge_base_path = knowledge_base_path
        
        # Initialisiere den Langchain-Agenten
        self.langchain_agent = PenetrationTestAgent(
            knowledge_base_path=knowledge_base_path,
            model_name=langchain_model,
            temperature=langchain_temperature
        )
        
        # Initialisiere die AutoGen-Agenten
        self.autogen_agents = BugBountyAgents(
            temperature=autogen_temperature,
            model=autogen_model
        )
    
    def add_knowledge_to_base(self, content: str, filename: str) -> bool:
        """
        Fügt Wissen zur Wissensdatenbank hinzu
        
        Args:
            content: Der Inhalt des Dokuments
            filename: Der Dateiname für das Dokument
            
        Returns:
            True, wenn erfolgreich hinzugefügt, sonst False
        """
        return self.langchain_agent.add_document_to_knowledge_base(content, filename)
    
    def analyze_bug_bounty_task(self, task: str, fetch_knowledge: bool = True) -> Dict[str, Any]:
        """
        Analysiert eine Bug-Bounty-Aufgabe mithilfe des Langchain-Agenten und der AutoGen-Agenten
        
        Args:
            task: Die zu analysierende Bug-Bounty-Aufgabe
            fetch_knowledge: Ob zuerst relevantes Wissen über den Langchain-Agenten abgerufen werden soll
            
        Returns:
            Ein Wörterbuch mit den Ergebnissen der Analyse
        """
        results = {
            "task": task,
            "langchain_insights": None,
            "autogen_plan": None,
            "combined_strategy": None
        }
        
        # Schritt 1: Verwende den Langchain-Agenten, um Wissen aus der Wissensdatenbank abzurufen
        if fetch_knowledge:
            knowledge_query = f"Sammle relevante Informationen für die folgende Bug-Bounty-Aufgabe: {task}"
            langchain_response = self.langchain_agent.run(knowledge_query)
            results["langchain_insights"] = langchain_response
        
        # Schritt 2: Erweitere die Aufgabe mit dem abgerufenen Wissen
        enhanced_task = task
        if fetch_knowledge and results["langchain_insights"]:
            enhanced_task = f"""
            {task}
            
            Relevante Informationen aus der Wissensdatenbank:
            {results["langchain_insights"]}
            """
        
        # Schritt 3: Starte die Zusammenarbeit der AutoGen-Agenten mit der erweiterten Aufgabe
        autogen_messages = self.autogen_agents.start_collaboration(enhanced_task)
        
        # Extrahiere den endgültigen Plan vom TeamLeadAgent
        final_plan = None
        for msg in reversed(autogen_messages):
            if msg.get("name") == "TeamLeadAgent":
                final_plan = msg.get("content")
                break
        
        results["autogen_plan"] = final_plan
        
        # Schritt 4: Zusammenfassung der kombinierten Strategie durch den Langchain-Agenten
        if results["langchain_insights"] and results["autogen_plan"]:
            summary_query = f"""
            Basierend auf dem abgerufenen Wissen und dem entwickelten Plan, erstelle eine zusammenfassende
            Strategie für die folgende Bug-Bounty-Aufgabe:
            
            Aufgabe: {task}
            
            Abgerufenes Wissen:
            {results["langchain_insights"]}
            
            Entwickelter Plan vom AutoGen-Team:
            {results["autogen_plan"]}
            
            Fasse die Schlüsselkomponenten zu einer umfassenden Bug-Bounty-Strategie zusammen.
            """
            
            combined_strategy = self.langchain_agent.run(summary_query)
            results["combined_strategy"] = combined_strategy
        
        return results
    
    def iterative_refinement(self, task: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Führt einen iterativen Verfeinerungsprozess für eine Bug-Bounty-Aufgabe durch
        
        Args:
            task: Die zu verfeinernde Bug-Bounty-Aufgabe
            max_iterations: Maximale Anzahl an Iterationen
            
        Returns:
            Ein Wörterbuch mit den Ergebnissen der iterativen Verfeinerung
        """
        results = {
            "task": task,
            "iterations": []
        }
        
        current_task = task
        
        for i in range(max_iterations):
            print(f"Iteration {i+1}/{max_iterations}...")
            
            # Analysiere die aktuelle Aufgabe
            iteration_result = self.analyze_bug_bounty_task(current_task)
            
            # Füge die Iterationsergebnisse hinzu
            results["iterations"].append({
                "iteration": i+1,
                "task": current_task,
                "result": iteration_result
            })
            
            # Verwende den Langchain-Agenten, um die Aufgabe für die nächste Iteration zu verfeinern
            if i < max_iterations - 1 and iteration_result["combined_strategy"]:
                refinement_query = f"""
                Basierend auf den bisherigen Ergebnissen, identifiziere Bereiche, die weiter untersucht werden sollten,
                und formuliere eine verfeinerte Aufgabe für die nächste Iteration:
                
                Ursprüngliche Aufgabe: {task}
                
                Kombinierte Strategie aus der aktuellen Iteration:
                {iteration_result["combined_strategy"]}
                
                Formuliere eine spezifischere und fokussiertere Aufgabe für die nächste Iteration.
                """
                
                refined_task = self.langchain_agent.run(refinement_query)
                current_task = refined_task
        
        # Füge eine Gesamtzusammenfassung hinzu
        final_summary_query = f"""
        Analysiere die Ergebnisse aller {max_iterations} Iterationen und erstelle eine umfassende
        Zusammenfassung der Bug-Bounty-Strategie:
        
        Ursprüngliche Aufgabe: {task}
        
        Iterationen:
        {json.dumps([iter["result"]["combined_strategy"] for iter in results["iterations"] if iter["result"]["combined_strategy"]], indent=2)}
        
        Erstelle eine strukturierte und umfassende Bug-Bounty-Strategie auf Basis aller Iterationen.
        """
        
        final_summary = self.langchain_agent.run(final_summary_query)
        results["final_strategy"] = final_summary
        
        return results


# Beispielverwendung
if __name__ == "__main__":
    # Initialisiere den Hybrid-Agent-Manager
    manager = HybridAgentManager()
    
    # Füge ein Beispieldokument hinzu, falls die Wissensdatenbank leer ist
    example_content = """
    # OWASP Top 10 Web-Anwendungs-Schwachstellen
    
    1. Injection (SQL, NoSQL, OS, etc.)
       - Ungefilterter Benutzereingaben führen zur Ausführung von Code
       - Prävention: Eingabevalidierung, Prepared Statements, ORM
    
    2. Fehlerhafte Authentifizierung
       - Schwache Passwörter, schlecht implementierte Session-Verwaltung
       - Prävention: Multi-Faktor-Authentifizierung, sichere Session-Verwaltung
    
    3. Sensitive Datenoffenlegung
       - Unsachgemäße Verschlüsselung sensibler Daten
       - Prävention: Starke Verschlüsselung, TLS, Datensicherheitsklassifizierung
    
    4. XML External Entities (XXE)
       - Verarbeitung von XML-Eingaben ohne Entitätsvalidierung
       - Prävention: DTD deaktivieren, Eingabevalidierung
    
    5. Fehlerhafte Zugriffskontrolle
       - Unzureichende Durchsetzung von Zugriffsrechten
       - Prävention: Implement Least Privilege, RBAC
    
    6. Sicherheitsfehlkonfiguration
       - Ungesicherte Standardkonfigurationen, offene Cloud-Speicher
       - Prävention: Härtung, Minimal-Konfiguration, Automatisierung
    
    7. Cross-Site Scripting (XSS)
       - Clientseitige Skriptinjektion durch Benutzer
       - Prävention: Output-Encoding, Content-Security-Policy
    
    8. Unsichere Deserialisierung
       - Deserialisierung nicht vertrauenswürdiger Daten
       - Prävention: Signierung serialisierter Objekte, Integritätsprüfungen
    
    9. Verwendung von Komponenten mit bekannten Schwachstellen
       - Veraltete Bibliotheken, Frameworks und andere Software
       - Prävention: Patch-Management, Verwaltung von Abhängigkeiten
    
    10. Unzureichende Protokollierung und Überwachung
        - Fehlen von Monitoring und incident Response
        - Prävention: Logging, Echtzeit-Monitoring, Incident-Response-Plan
    """
    manager.add_knowledge_to_base(example_content, "owasp_top10.txt")
    
    # Beispielaufgabe
    task = """
    Entwickle eine Bug-Bounty-Strategie für eine mittelgroße E-Commerce-Website, die auf einem LAMP-Stack
    (Linux, Apache, MySQL, PHP) basiert. Die Website verwendet auch das Bootstrap-Framework für das Frontend
    und verfügt über Benutzerregistrierung, Login-Funktionalität, Warenkorbsystem und Zahlungsabwicklung.
    Wir haben die Erlaubnis, passive Aufklärung und nicht-invasive Scans durchzuführen.
    """
    
    # Führe eine einfache Analyse durch
    results = manager.analyze_bug_bounty_task(task)
    
    print("\n--- ERGEBNISSE DER ANALYSE ---\n")
    if results["langchain_insights"]:
        print("\n--- LANGCHAIN-ERKENNTNISSE ---\n")
        print(results["langchain_insights"])
    
    if results["autogen_plan"]:
        print("\n--- AUTOGEN-PLAN ---\n")
        print(results["autogen_plan"])
    
    if results["combined_strategy"]:
        print("\n--- KOMBINIERTE STRATEGIE ---\n")
        print(results["combined_strategy"]) 