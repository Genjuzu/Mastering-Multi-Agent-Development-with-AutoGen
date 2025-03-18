"""
AutoGen-Agenten für spezifische Bug-Bounty-Aufgaben
"""

import os
import autogen
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

class BugBountyAgents:
    """Manager für AutoGen-Agenten für Bug-Bounty-Aufgaben"""
    
    def __init__(self,
                temperature: float = 0.7,
                model: str = "gpt-3.5-turbo"):
        """
        Initialisiert die Bug-Bounty-Agenten
        
        Args:
            temperature: Temperatur für die Agenten-LLMs
            model: Name des LLM-Modells
        """
        self.temperature = temperature
        self.model = model
        
        # Konfiguration für alle Agenten
        self.config_list = [
            {
                "model": model,
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        ]
        
        # Initialisiere alle Agenten
        self.reconnaissance_agent = self._create_reconnaissance_agent()
        self.vulnerability_scanner_agent = self._create_vulnerability_scanner_agent()
        self.exploit_planner_agent = self._create_exploit_planner_agent()
        self.team_lead_agent = self._create_team_lead_agent()
        
        # Gruppenchat für die Agenten
        self.group_chat = self._setup_group_chat()
    
    def _create_reconnaissance_agent(self):
        """Erstellt den Aufklärungsagenten"""
        reconnaissance_agent = autogen.AssistantAgent(
            name="ReconAgent",
            system_message="""Du bist ein Experte für Aufklärung und Informationssammlung in Bug-Bounty-Szenarien.
            Deine Hauptaufgabe ist die Identifizierung von Informationen über das Zielsystem, einschließlich:
            - Domäneninformationen und DNS-Einträge
            - Öffentlich zugängliche Dienste und Ports
            - Technologiestack und bekannte Software
            - Netzwerkarchitektur und Infrastruktur
            
            Deine Antworten sollten detaillierte Strategien zur Informationssammlung und Werkzeuge wie nmap, dig, whois, theHarvester, Shodan usw. umfassen.
            Stelle konkrete Befehle und deren erwartete Ausgabe bereit, wenn möglich.
            """,
            llm_config={"config_list": self.config_list, "temperature": self.temperature}
        )
        return reconnaissance_agent
    
    def _create_vulnerability_scanner_agent(self):
        """Erstellt den Schwachstellen-Scanner-Agenten"""
        vulnerability_scanner_agent = autogen.AssistantAgent(
            name="VulnScanAgent",
            system_message="""Du bist ein Experte für die Identifizierung und Analyse von Schwachstellen in Bug-Bounty-Szenarien.
            Deine Hauptaufgabe ist die Identifizierung potenzieller Schwachstellen im Zielsystem, einschließlich:
            - Automatisiertes Scannen mit Werkzeugen wie Nessus, OpenVAS, Nikto
            - Identifizierung von häufigen Schwachstellen (OWASP Top 10, CWEs, etc.)
            - Priorisierung von Schwachstellen basierend auf Risiko und Auswirkung
            - Manuelle Überprüfung und Validierung von Schwachstellen
            
            Liefere genaue Anweisungen zur Überprüfung und Validierung von Schwachstellen und erkläre die potenziellen Auswirkungen und Risiken.
            """,
            llm_config={"config_list": self.config_list, "temperature": self.temperature}
        )
        return vulnerability_scanner_agent
    
    def _create_exploit_planner_agent(self):
        """Erstellt den Exploit-Planer-Agenten"""
        exploit_planner_agent = autogen.AssistantAgent(
            name="ExploitAgent",
            system_message="""Du bist ein Experte für die Entwicklung von Ausnutzungsstrategien für Schwachstellen in Bug-Bounty-Szenarien.
            Deine Hauptaufgabe ist die Planung von Proof-of-Concept-Exploits, einschließlich:
            - Entwicklung von Ausnutzungsstrategien für identifizierte Schwachstellen
            - Erstellung von Proof-of-Concept-Code oder Payload
            - Risikoabschätzung und Einschätzung der Auswirkungen
            - Ethische Überlegungen und verantwortungsvolle Offenlegung
            
            WICHTIG: Deine Antworten sollten NIEMALS tatsächlich schädlichen Code enthalten, sondern theoretische Konzepte und Pseudocode
            für das Verständnis der Schwachstelle. Der Zweck ist die Demonstration der Schwachstelle für die Behebung,
            nicht die tatsächliche Ausnutzung für schädliche Zwecke.
            """,
            llm_config={"config_list": self.config_list, "temperature": self.temperature}
        )
        return exploit_planner_agent
    
    def _create_team_lead_agent(self):
        """Erstellt den Team-Lead-Agenten"""
        team_lead_agent = autogen.AssistantAgent(
            name="TeamLeadAgent",
            system_message="""Du bist der leitende Koordinator für Bug-Bounty-Aktivitäten.
            Deine Hauptaufgabe ist die Koordination und Leitung des Teams von Spezialagenten, einschließlich:
            - Festlegung der Gesamtstrategie und Priorisierung von Aufgaben
            - Verteilung von Aufgaben an die geeigneten Spezialagenten
            - Analyse und Zusammenfassung der Ergebnisse der Spezialagenten
            - Entwicklung eines umfassenden Bug-Bounty-Berichts
            
            Du sollst klare Anweisungen geben, den Fortschritt überwachen und sicherstellen, dass alle
            Bug-Bounty-Aktivitäten ethisch und innerhalb der festgelegten Grenzen durchgeführt werden.
            """,
            llm_config={"config_list": self.config_list, "temperature": self.temperature}
        )
        return team_lead_agent
    
    def _setup_group_chat(self):
        """Richtet einen Gruppenchat für die Zusammenarbeit der Agenten ein"""
        # Erstelle einen menschlichen Proxy-Agenten für die Interaktion
        user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "agent_workspace"}
        )
        
        # Erstelle einen Gruppenchat mit allen Agenten
        group_chat = autogen.GroupChat(
            agents=[
                user_proxy, 
                self.team_lead_agent,
                self.reconnaissance_agent,
                self.vulnerability_scanner_agent,
                self.exploit_planner_agent
            ],
            messages=[],
            max_round=50
        )
        
        # Erstelle einen Manager für den Gruppenchat
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config={"config_list": self.config_list, "temperature": self.temperature}
        )
        
        return {
            "group_chat": group_chat,
            "manager": manager,
            "user_proxy": user_proxy
        }
    
    def start_collaboration(self, task: str) -> List[Dict[str, Any]]:
        """
        Startet eine Zusammenarbeit zwischen den Agenten für eine bestimmte Aufgabe
        
        Args:
            task: Die Aufgabe, an der die Agenten arbeiten sollen
            
        Returns:
            Die Nachrichten aus dem Gruppenchat
        """
        try:
            # Starte die Zusammenarbeit mit der Aufgabe
            self.group_chat["user_proxy"].initiate_chat(
                self.group_chat["manager"],
                message=f"""
                Wir arbeiten an einem Bug-Bounty-Projekt mit folgender Aufgabe:
                
                {task}
                
                Bitte entwickelt einen Plan zur Lösung dieser Aufgabe. Der TeamLeadAgent sollte die Diskussion koordinieren.
                Jeder Agent sollte seine spezifischen Fähigkeiten und sein Fachwissen einbringen.
                
                Nach der Diskussion fasst der TeamLeadAgent die Ergebnisse zusammen und erstellt einen Aktionsplan.
                """
            )
            
            # Gib die Chat-Nachrichten zurück
            return self.group_chat["group_chat"].messages
        except Exception as e:
            print(f"Fehler beim Starten der Zusammenarbeit: {e}")
            return []
    
    def add_agent_to_chat(self, name: str, system_message: str) -> bool:
        """
        Fügt einen benutzerdefinierten Agenten zum Gruppenchat hinzu
        
        Args:
            name: Name des Agenten
            system_message: Systemnachricht für den Agenten
            
        Returns:
            True, wenn erfolgreich hinzugefügt, sonst False
        """
        try:
            # Erstelle einen neuen Agenten
            new_agent = autogen.AssistantAgent(
                name=name,
                system_message=system_message,
                llm_config={"config_list": self.config_list, "temperature": self.temperature}
            )
            
            # Füge den Agenten zum Gruppenchat hinzu
            self.group_chat["group_chat"].agents.append(new_agent)
            
            return True
        except Exception as e:
            print(f"Fehler beim Hinzufügen des Agenten: {e}")
            return False


# Beispielverwendung
if __name__ == "__main__":
    agents = BugBountyAgents()
    
    # Starte einen Beispiel-Kollaborationsprozess
    task = """
    Analyse der Website example.com auf Schwachstellen. Wir haben die Erlaubnis, passive Aufklärung
    und nicht-invasive Scans durchzuführen. Entwickelt eine Strategie für die Aufklärungsphase
    und die Identifizierung potenzieller Schwachstellen.
    """
    
    messages = agents.start_collaboration(task)
    
    # Ausgabe der letzten Nachricht (Zusammenfassung vom TeamLeadAgent)
    for msg in reversed(messages):
        if msg.get("name") == "TeamLeadAgent":
            print("Endgültiger Plan vom TeamLeadAgent:")
            print(msg.get("content"))
            break 