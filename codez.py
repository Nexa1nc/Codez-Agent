import os
import requests
import subprocess
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Inizializzazione della console per i colori e lo stile
console = Console()

def logo():
    """Pulisce lo schermo e stampa il logo ASCII."""
    os.system('cls' if os.name == 'nt' else 'clear')
    # Usiamo r""" per evitare che i backslash vengano interpretati male
    ascii_art = r"""
 [bold cyan]
  /$$$$$$                  /$$                     
 /$$__  $$                | $$                     
| $$  \__/  /$$$$$$   /$$$$$$$  /$$$$$$  /$$$$$$$$ 
| $$       /$$__  $$ /$$__  $$ /$$__  $$|____ /$$/ 
| $$      | $$  \ $$| $$  | $$| $$$$$$$$   /$$$$/  
| $$    $$| $$  \ $$| $$  | $$| $$_____/  /$$__/   
|  $$$$$$/|  $$$$$$/|  $$$$$$$|  $$$$$$$ /$$$$$$$$ 
 \______/  \______/  \_______/ \_______/|________/ 
 [/bold cyan]
    """
    console.print(Panel(ascii_art, border_style="cyan", title="AI AGENT TERMINAL"))

def configura_sessione():
    """Gestisce la scelta del provider e del modello."""
    console.print("\n[italic]Digita 'ollama' per locale, oppure incolla la tua API Key (Groq/OpenAI)[/italic]")
    key = input("Chiave o 'ollama': ").strip()
    
    if key.lower() == "ollama":
        prov, url = "Ollama", "http://localhost:11434/v1"
    elif key.startswith("gsk_"):
        prov, url = "Groq", "https://api.groq.com/openai/v1"
    else:
        prov, url = "OpenAI", "https://api.openai.com/v1"
    
    headers = {"Authorization": f"Bearer {key}"} if key.lower() != "ollama" else {}
    
    # Tentativo di recupero modelli disponibili
    try:
        r = requests.get(f"{url}/models", headers=headers, timeout=2)
        if r.status_code == 200:
            modelli = [m['id'] for m in r.json()['data']][:10]
        else:
            modelli = ["gpt-4o", "llama3", "mistral", "phi3"]
    except:
        modelli = ["gpt-4o", "llama3", "mistral", "phi3"]

    console.print("\n[bold yellow]Modelli disponibili:[/bold yellow]")
    for i, m in enumerate(modelli):
        console.print(f"{i+1}. {m}")
    
    scelta = int(Prompt.ask("\nScegli il numero del modello", default="1")) - 1
    return key, prov, url, modelli[scelta]

def esegui_comando(comando):
    """Esegue un comando sul terminale dopo conferma dell'utente."""
    console.print(f"\n[bold orange3]L'AI vuole eseguire:[/bold orange3] [green]{comando}[/green]")
    conferma = Prompt.ask("Vuoi procedere?", choices=["y", "n"], default="n")
    
    if conferma == "y":
        try:
            res = subprocess.run(comando, shell=True, capture_output=True, text=True)
            console.print("[bold green]Eseguito con successo.[/bold green]")
            return f"Output: {res.stdout}\nErrori: {res.stderr}"
        except Exception as e:
            return f"Errore durante l'esecuzione: {e}"
    return "Esecuzione annullata dall'utente."

def main():
    """Funzione principale che avvia il programma."""
    logo()
    key, prov, url, mod = configura_sessione()
    
    console.print(f"\n[bold green]CONNESSO A: {prov} ({mod})[/bold green]")
    console.print("[dim]Comandi speciali: /stop (esci), /change (cambia modello)[/dim]\n")

    while True:
        user_input = input(f"({mod}) > ").strip()
        
        if not user_input:
            continue
            
        if user_input == "/stop":
            console.print("[bold red]Chiusura in corso... Ciao![/bold red]")
            break
            
        if user_input == "/change":
            key, prov, url, mod = configura_sessione()
            console.print(f"\n[bold green]Passato a: {prov} ({mod})[/bold green]")
            continue

        # Logica della richiesta AI
        prompt_sistema = (
            "Sei Codez, un assistente terminale. "
            "Se l'utente ti chiede di fare qualcosa sul PC (creare file, cartelle, ecc.), "
            "rispondi SOLO con 'COMMAND: ' seguito dal comando da eseguire. "
            "Altrimenti rispondi normalmente."
        )
        
        payload = {
            "model": mod,
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": user_input}
            ]
        }
        
        try:
            h = {"Authorization": f"Bearer {key}"} if key.lower() != "ollama" else {}
            r = requests.post(f"{url}/chat/completions", headers=h, json=payload)
            r.raise_for_status()
            risposta = r.json()['choices'][0]['message']['content']

            if "COMMAND: " in risposta:
                cmd = risposta.split("COMMAND: ")[1].strip()
                # Rimuove eventuali virgolette se l'AI le aggiunge per errore
                cmd = cmd.replace('`', '') 
                esito = esegui_comando(cmd)
                console.print(f"[dim]{esito}[/dim]")
            else:
                console.print(f"\n[bold cyan]AI:[/bold cyan] {risposta}\n")
                
        except Exception as e:
            console.print(f"[bold red]Errore di connessione:[/bold red] {e}")
            console.print("[yellow]Assicurati che Ollama sia attivo o che la Key sia corretta.[/yellow]")

if __name__ == "__main__":
    main()