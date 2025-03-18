# AutoGenchain - WiFi/Netzwerk-Sicherheitsframework

Ein modulares KI-gestütztes Framework zur Analyse von WiFi- und Netzwerksicherheit, das Langchain für die Wissensintegration und AutoGen für die Agentenkooperation verwendet.

## Überblick

AutoGenchain kombiniert die Stärken von Langchain (Retrieval-Augmented Generation) und AutoGen (multi-agent Kooperation) für ein leistungsstarkes Framework zur Planung und Analyse von:

- WiFi-Netzwerksicherheit
- Penetrationstests
- Bug-Bounty-Programmen
- Sicherheitsassessments

Das System integriert eine umfangreiche Wissensdatenbank zu Sicherheitsthemen und nutzt spezialisierte KI-Agenten für verschiedene Aspekte der Sicherheitsanalyse.

## Projektstruktur

```
AutoGenchain/
├── README.md                   # Hauptdokumentation
├── .env                        # Umgebungsvariablen (API-Schlüssel usw.)
├── main.py                     # Haupt-Einstiegspunkt der Anwendung
├── requirements.txt            # Python-Abhängigkeiten
├── setup_env.py                # Setup-Hilfsskript
│
├── config/                     # Konfigurationsdateien
│   ├── agent_config.json       # Konfigurationen für KI-Agenten
│   └── system_config.json      # Systemkonfigurationen
│
├── data/                       # Datenspeicher und -ausgabe
│   ├── results/                # Analyseergebnisse
│   └── temp/                   # Temporäre Dateien
│
├── knowledge_base/             # Wissensdatenbank
│   ├── wifi/                   # WiFi-spezifisches Wissen
│   │   ├── wifi_network_hacking.txt
│   │   └── wifi_hacking_practical.txt
│   ├── web/                    # Web-Sicherheitswissen
│   │   ├── owasp_top10.txt
│   │   └── web_app_security.txt
│   └── general/                # Allgemeines Sicherheitswissen
│       ├── pentest_methodology.txt
│       ├── bug_bounty_programs.txt
│       └── common_exploits.txt
│
├── src/                        # Quellcode
│   ├── agents/                 # Agentenmodule
│   │   ├── langchain_agent.py  # Langchain-basierter Wissensagent
│   │   ├── autogen_agents.py   # AutoGen-basierte Agentengruppe
│   │   └── integration.py      # Integration der Agentensysteme
│   │
│   ├── utils/                  # Hilfsfunktionen
│   │   ├── knowledge_utils.py  # Wissensdatenbankfunktionen
│   │   └── security_utils.py   # Sicherheitsbezogene Hilfsfunktionen
│   │
│   └── tests/                  # Tests
│       └── test_knowledge_base.py  # Test für die Wissensdatenbank
```

## Installation

1. Repository klonen:
```bash
git clone https://github.com/username/AutoGenchain.git
cd AutoGenchain
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. `.env`-Datei einrichten:
```
OPENAI_API_KEY=your_openai_api_key_here
MAIN_AGENT_TEMPERATURE=0.2
AUTOGEN_TEMPERATURE=0.7
KNOWLEDGE_BASE_PATH=./knowledge_base
```

## Verwendung

### Kommandozeilenschnittstelle

Das Framework bietet eine Kommandozeilenschnittstelle mit verschiedenen Befehlen:

```bash
# Analyse einer Bug-Bounty-Aufgabe
python main.py analyze --task "Finde Schwachstellen im WPA2-Authentifizierungsprozess"

# Iterative Verfeinerung einer Sicherheitsaufgabe
python main.py refine --task "Entwickle eine Strategie für WiFi-Pentesting" --iterations 3

# Wissen zur Wissensdatenbank hinzufügen
python main.py add-knowledge --file path/to/knowledge.txt --name "new_knowledge.txt"

# Interaktiver Modus
python main.py interactive
```

### Testen der Wissensdatenbank

Um die Wissensdatenbank zu testen:

```bash
python src/tests/test_knowledge_base.py
```

## Hauptkomponenten

### 1. Wissensdatenbank (Langchain RAG)
Eine umfangreiche Sammlung von Dokumenten zu verschiedenen Sicherheitsthemen, die durch Langchain's Retrieval-Augmented Generation (RAG) zugänglich gemacht wird.

### 2. Agentensystem (AutoGen)
Ein Team spezialisierter Agenten, die zusammenarbeiten, um Sicherheitsaufgaben zu analysieren und zu lösen:
- Sicherheitsexperte
- Angreifer
- Verteidiger
- Planer

### 3. Hybridmanager (Integration)
Koordiniert die Zusammenarbeit zwischen der Wissensdatenbank und dem Agentensystem, um optimale Ergebnisse zu erzielen.

## Beispiele

### WiFi-Sicherheitsanalyse
```bash
python main.py analyze --task "Identifiziere Schwachstellen in einem WPA2-Enterprise-Netzwerk mit RADIUS-Server"
```

### Bug-Bounty-Planung
```bash
python main.py analyze --task "Plane eine Strategie für ein Bug-Bounty-Programm für eine E-Commerce-Website"
```

## Erweiterung der Wissensdatenbank

Die Wissensdatenbank kann einfach erweitert werden:

```bash
python main.py add-knowledge --content "Detaillierte Informationen zu neuen Sicherheitsthemen..." --name "neues_thema.txt"
```

## Lizenz

MIT-Lizenz

## Haftungsausschluss

Dieses Tool dient ausschließlich zu Bildungs- und legitimen Sicherheitstestzwecken. Die Verwendung für nicht autorisierte Sicherheitstests oder Angriffe ist illegal und unethisch. 