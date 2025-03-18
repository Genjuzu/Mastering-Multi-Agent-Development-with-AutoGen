"""
Hauptskript für das Bug-Bounty-Hybrid-Agentensystem mit Langchain und AutoGen
"""

import os
import argparse
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Importiere unsere benutzerdefinierten Module
from integration import HybridAgentManager

# Lade Umgebungsvariablen
load_dotenv()

def setup_argument_parser():
    """Richtet den Argument-Parser für die Kommandozeile ein"""
    parser = argparse.ArgumentParser(description="Bug-Bounty-Hybrid-Agentensystem mit Langchain und AutoGen")
    
    # Hauptbefehle
    subparsers = parser.add_subparsers(dest="command", help="Befehl, der ausgeführt werden soll")
    
    # Befehl: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analysiere eine Bug-Bounty-Aufgabe")
    analyze_parser.add_argument("--task", type=str, required=True, help="Die zu analysierende Bug-Bounty-Aufgabe")
    analyze_parser.add_argument("--output", type=str, help="Pfad für die Ausgabedatei (JSON)")
    analyze_parser.add_argument("--no-knowledge", action="store_true", help="Kein Wissen aus der Wissensdatenbank abrufen")
    
    # Befehl: refine
    refine_parser = subparsers.add_parser("refine", help="Führe eine iterative Verfeinerung einer Bug-Bounty-Aufgabe durch")
    refine_parser.add_argument("--task", type=str, required=True, help="Die zu verfeinernde Bug-Bounty-Aufgabe")
    refine_parser.add_argument("--iterations", type=int, default=3, help="Anzahl der Iterationen (Standard: 3)")
    refine_parser.add_argument("--output", type=str, help="Pfad für die Ausgabedatei (JSON)")
    
    # Befehl: add-knowledge
    add_knowledge_parser = subparsers.add_parser("add-knowledge", help="Füge Wissen zur Wissensdatenbank hinzu")
    add_knowledge_parser.add_argument("--file", type=str, help="Pfad zur Eingabedatei")
    add_knowledge_parser.add_argument("--content", type=str, help="Inhalt, der direkt hinzugefügt werden soll")
    add_knowledge_parser.add_argument("--name", type=str, required=True, help="Name der Wissensdatei")
    
    # Befehl: interactive
    subparsers.add_parser("interactive", help="Starte den interaktiven Modus")
    
    return parser

def save_results(results: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Speichert die Ergebnisse in einer JSON-Datei
    
    Args:
        results: Die zu speichernden Ergebnisse
        output_path: Pfad für die Ausgabedatei (optional)
        
    Returns:
        Der Pfad zur gespeicherten Datei
    """
    if not output_path:
        # Erstelle einen Standardpfad, wenn keiner angegeben ist
        if not os.path.exists("./results"):
            os.makedirs("./results")
        
        # Erzeuge einen eindeutigen Dateinamen basierend auf Zeitstempel
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"./results/bugbounty_results_{timestamp}.json"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Ergebnisse wurden gespeichert unter: {output_path}")
        return output_path
    except Exception as e:
        print(f"Fehler beim Speichern der Ergebnisse: {e}")
        return ""

def print_results(results: Dict[str, Any]) -> None:
    """
    Gibt die Analyseergebnisse auf der Konsole aus
    
    Args:
        results: Die auszugebenden Ergebnisse
    """
    print("\n" + "="*80)
    print("BUG-BOUNTY-ANALYSE-ERGEBNISSE")
    print("="*80 + "\n")
    
    print(f"AUFGABE: {results.get('task', 'Keine Aufgabe angegeben')}\n")
    
    if "langchain_insights" in results and results["langchain_insights"]:
        print("-"*80)
        print("ERKENNTNISSE AUS DER WISSENSDATENBANK")
        print("-"*80)
        print(results["langchain_insights"])
        print()
    
    if "autogen_plan" in results and results["autogen_plan"]:
        print("-"*80)
        print("PLAN DES AUTOGEN-TEAMS")
        print("-"*80)
        print(results["autogen_plan"])
        print()
    
    if "combined_strategy" in results and results["combined_strategy"]:
        print("-"*80)
        print("KOMBINIERTE STRATEGIE")
        print("-"*80)
        print(results["combined_strategy"])
        print()
    
    if "iterations" in results:
        print("-"*80)
        print(f"ITERATIVE VERFEINERUNG ({len(results['iterations'])} Iterationen)")
        print("-"*80)
        
        for i, iteration in enumerate(results["iterations"]):
            print(f"\nITERATION {i+1}:")
            print(f"Aufgabe: {iteration['task']}")
            
            if "result" in iteration and "combined_strategy" in iteration["result"]:
                print("\nStrategie:")
                print(iteration["result"]["combined_strategy"])
        
        if "final_strategy" in results:
            print("\n" + "="*80)
            print("ENDGÜLTIGE STRATEGIE")
            print("="*80)
            print(results["final_strategy"])
    
    print("\n" + "="*80 + "\n")

def interactive_mode() -> None:
    """Startet den interaktiven Modus für das Bug-Bounty-System"""
    print("\n" + "="*80)
    print("BUG-BOUNTY-HYBRID-AGENTENSYSTEM - INTERAKTIVER MODUS")
    print("="*80 + "\n")
    
    # Initialisiere den Hybrid-Agent-Manager
    manager = HybridAgentManager()
    
    print("Willkommen zum Bug-Bounty-Hybrid-Agentensystem!")
    print("Dieses System kombiniert Langchain- und AutoGen-Agenten für Bug-Bounty-Planung.")
    print("Geben Sie 'exit' oder 'quit' ein, um den interaktiven Modus zu beenden.\n")
    
    while True:
        print("\nVerfügbare Befehle:")
        print("1. analyze - Analysiere eine Bug-Bounty-Aufgabe")
        print("2. refine - Führe eine iterative Verfeinerung durch")
        print("3. add-knowledge - Füge Wissen zur Wissensdatenbank hinzu")
        print("4. exit - Beende den interaktiven Modus")
        
        command = input("\nBefehl: ").strip().lower()
        
        if command in ["exit", "quit", "4"]:
            print("Auf Wiedersehen!")
            break
        
        elif command in ["analyze", "1"]:
            task = input("\nGeben Sie die Bug-Bounty-Aufgabe ein: ").strip()
            use_knowledge = input("Wissen aus der Wissensdatenbank abrufen? (j/n): ").strip().lower()
            
            fetch_knowledge = use_knowledge.startswith("j")
            
            print("\nAnalyse wird durchgeführt... (Dies kann einige Zeit dauern)")
            results = manager.analyze_bug_bounty_task(task, fetch_knowledge=fetch_knowledge)
            
            print_results(results)
            
            save_option = input("Möchten Sie die Ergebnisse speichern? (j/n): ").strip().lower()
            if save_option.startswith("j"):
                output_path = input("Pfad für die Ausgabedatei (leer lassen für Standardpfad): ").strip()
                save_results(results, output_path if output_path else None)
        
        elif command in ["refine", "2"]:
            task = input("\nGeben Sie die Bug-Bounty-Aufgabe ein: ").strip()
            iterations_input = input("Anzahl der Iterationen (Standard: 3): ").strip()
            
            try:
                iterations = int(iterations_input) if iterations_input else 3
            except ValueError:
                print("Ungültige Eingabe. Standard (3) wird verwendet.")
                iterations = 3
            
            print(f"\nIterative Verfeinerung mit {iterations} Iterationen wird durchgeführt... (Dies kann einige Zeit dauern)")
            results = manager.iterative_refinement(task, max_iterations=iterations)
            
            print_results(results)
            
            save_option = input("Möchten Sie die Ergebnisse speichern? (j/n): ").strip().lower()
            if save_option.startswith("j"):
                output_path = input("Pfad für die Ausgabedatei (leer lassen für Standardpfad): ").strip()
                save_results(results, output_path if output_path else None)
        
        elif command in ["add-knowledge", "3"]:
            name = input("\nName der Wissensdatei (z.B. sql_injection.txt): ").strip()
            
            content_source = input("Inhalt aus Datei laden oder direkt eingeben? (datei/eingabe): ").strip().lower()
            
            if content_source.startswith("d"):
                file_path = input("Pfad zur Datei: ").strip()
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    success = manager.add_knowledge_to_base(content, name)
                    
                    if success:
                        print(f"Wissen aus {file_path} wurde erfolgreich zur Wissensdatenbank hinzugefügt.")
                    else:
                        print("Fehler beim Hinzufügen des Wissens.")
                
                except Exception as e:
                    print(f"Fehler beim Lesen der Datei: {e}")
            
            else:
                print("Geben Sie den Inhalt ein (beenden mit '###' in einer neuen Zeile):")
                content_lines = []
                
                while True:
                    line = input()
                    if line.strip() == "###":
                        break
                    content_lines.append(line)
                
                content = "\n".join(content_lines)
                
                success = manager.add_knowledge_to_base(content, name)
                
                if success:
                    print(f"Wissen wurde erfolgreich zur Wissensdatenbank hinzugefügt.")
                else:
                    print("Fehler beim Hinzufügen des Wissens.")
        
        else:
            print("Unbekannter Befehl. Bitte versuchen Sie es erneut.")

def main():
    """Hauptfunktion"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialisiere den Hybrid-Agent-Manager
    manager = HybridAgentManager()
    
    if args.command == "analyze":
        fetch_knowledge = not args.no_knowledge
        results = manager.analyze_bug_bounty_task(args.task, fetch_knowledge=fetch_knowledge)
        
        print_results(results)
        
        if args.output:
            save_results(results, args.output)
    
    elif args.command == "refine":
        results = manager.iterative_refinement(args.task, max_iterations=args.iterations)
        
        print_results(results)
        
        if args.output:
            save_results(results, args.output)
    
    elif args.command == "add-knowledge":
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Fehler beim Lesen der Datei: {e}")
                return
        elif args.content:
            content = args.content
        else:
            print("Entweder --file oder --content muss angegeben werden.")
            return
        
        success = manager.add_knowledge_to_base(content, args.name)
        
        if success:
            print(f"Wissen wurde erfolgreich zur Wissensdatenbank hinzugefügt: {args.name}")
        else:
            print("Fehler beim Hinzufügen des Wissens.")
    
    elif args.command == "interactive":
        interactive_mode()

if __name__ == "__main__":
    main() 