import os
import requests
import subprocess
import json
import psutil
import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Inizializzazione della console
console = Console()

def logo():
    """Pulisce lo schermo e stampa il logo ASCII."""
    os.system('cls' if os.name == 'nt' else 'clear')
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
    console.print(Panel(ascii_art, border_style="cyan", title="CODEZ AGENT v2.1 - Open Source & Accessible"))

def scrivi_log(comando, esito):
    """Salva i comandi riusciti in un file di testo locale (Principio: Educativo)."""
    orario = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("codez_history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{orario}] COMANDO: {comando}\n")
        f.write(f"ESITO: {esito[:150]}...\n")
        f.write("-" * 40 + "\n")

def system_doctor():
    """Monitora le risorse del sistema (Principio: Budget 0)."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    status = "[bold green]OK[/bold green]" if ram < 80 else "[bold red]FULL[/bold red]"
    info = f"💻 CPU: {cpu}% | 🧠 RAM: {ram}% | 📊 Stato: {status}"
    console.print(Panel(info, title="🏥 System Doctor", border_style="blue"))

def configura_sessione():
    """Scansione automatica modelli (Principio: Accessibilità)."""
    console.print("\n[italic]Digita 'ollama' o incolla la tua API Key[/italic]")
    key = input("Chiave: ").strip()
    
    if key.lower() == "ollama":
        prov, url = "Ollama", "http://localhost:11434/v1"
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            modelli = [m['name'] for m in r.json()['models']]
        except:
            modelli = ["llama3", "phi3", "mistral"]
    else:
        prov, url = "Cloud AI", "https://api.groq.com/openai/v1" if key.startswith("gsk_") else "https://api.openai.com/v1"
        modelli = ["gpt-4o", "llama3-70b-8192", "mixtral-8x7b-32768"]

    console.print("\n[bold yellow]Modelli Rilevati:[/bold yellow]")
    for i, m in enumerate(modelli):
        console.print(f"{i+1}. {m}")
    
    scelta = int(Prompt.ask("\nScegli numero", default="1")) - 1
    return key, prov, url, modelli[scelta]

def esegui_comando(comando):
    """Esegue comandi, salva i log e rileva errori di installazione."""
    console.print(f"\n[bold orange3]PROPOSTA:[/bold orange3] [white on blue] {comando} [/white on blue]")
    
    if Prompt.ask("Eseguire?", choices=["y", "n"], default="y") == "y":
        res = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        # Se il comando ha successo
        if res.returncode == 0:
            console.print("[bold green]Successo![/bold green]")
            scrivi_log(comando, res.stdout)
            return f"Output: {res.stdout}"
        
        # Se il comando fallisce (Auto-Installer Logic)
        else:
            errore = res.stderr.lower()
            if "not found" in errore or "non è riconosciuto" in errore:
                console.print(f"[bold red]ERRORE:[/bold red] Sembra che lo strumento per '{comando.split()[0]}' non sia installato.")
                console.print("[yellow]Suggerimento: Prova a chiedere a Codez come installarlo![/yellow]")
            return f"Errore: {res.stderr}"
            
    return "Annullato dall'utente."

def main():
    logo()
    key, prov, url, mod = configura_sessione()
    
    console.print(f"\n[bold green]Codez v2.1 Pronta! ({mod})[/bold green]")
    console.print("[dim]/status | /explain | /history (apre i log) | /stop[/dim]\n")

    ultimo_comando_proposto = ""

    while True:
        user_input = input(f"({mod}) > ").strip()
        
        if not user_input: continue
        if user_input == "/stop": break
        
        if user_input == "/status":
            system_doctor()
            continue

        if user_input == "/history":
            if os.path.exists("codez_history.txt"):
                os.system('notepad codez_history.txt' if os.name == 'nt' else 'open codez_history.txt')
            else:
                console.print("[yellow]Nessuna cronologia trovata.[/yellow]")
            continue

        if user_input == "/explain":
            if not ultimo_comando_proposto:
                console.print("[yellow]Nessun comando da spiegare![/yellow]")
                continue
            user_input = f"Spiegami come a un principiante cosa fa: {ultimo_comando_proposto}"

        # Richiesta all'IA
        prompt_sistema = (
            "Sei Codez, un assistente terminale per neofiti. "
            "Se devi agire sul PC rispondi SOLO con 'COMMAND: ' seguito dal comando. "
            "Se l'utente ha avuto un errore, suggerisci come installare i pacchetti mancanti (es. pip, brew, apt)."
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
            risposta = r.json()['choices'][0]['message']['content']

            if "COMMAND: " in risposta:
                cmd = risposta.split("COMMAND: ")[1].strip().replace('`', '')
                ultimo_comando_proposto = cmd
                esito = esegui_comando(cmd)
                console.print(f"[dim]{esito}[/dim]")
            else:
                console.print(f"\n[bold cyan]AI:[/bold cyan] {risposta}\n")
                
        except Exception as e:
            console.print(f"[red]Errore critico: {e}[/red]")

if __name__ == "__main__":
    main()